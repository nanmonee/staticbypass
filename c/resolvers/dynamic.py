import random
import string

class dynamic:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.typedefs = {
            "VirtualAlloc":"typedef LPVOID (WINAPI *VirtualAlloc_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);",
            "CreateThread":"typedef HANDLE (WINAPI *CreateThread_t)(LPSECURITY_ATTRIBUTES lpThreadAttributes, SIZE_T dwStackSize, LPTHREAD_START_ROUTINE lpStartAddress, LPVOID lpParameter, DWORD dwCreationFlags, LPDWORD lpThreadId);",
            "HeapAlloc":"typedef LPVOID (WINAPI *HeapAlloc_t)(HANDLE hHeap, DWORD dwFlags, SIZE_T dwBytes);",
            "HeapCreate":"typedef HANDLE (WINAPI *HeapCreate_t)(DWORD flOptions, SIZE_T dwInitialSize, SIZE_T dwMaximumSize);",
            "WriteProcessMemory":"typedef BOOL (WINAPI *WriteProcessMemory_t)(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize, SIZE_T *lpNumberOfBytesWritten);",
            "CreateProcessA":"typedef BOOL (WINAPI *CreateProcessA_t)(LPCSTR lpApplicationName, LPSTR lpCommandLine, LPSECURITY_ATTRIBUTES lpProcessAttributes, LPSECURITY_ATTRIBUTES lpThreadAttributes, BOOL bInheritHandles, DWORD dwCreationFlags, LPVOID lpEnvironment, LPCSTR lpCurrentDirectory, LPSTARTUPINFOA lpStartupInfo, LPPROCESS_INFORMATION lpProcessInformation);",
            "CloseHandle":"typedef BOOL (WINAPI *CloseHandle_t)(HANDLE hObject);",
            "WaitForSingleObject":"typedef DWORD (WINAPI *WaitForSingleObject_t)(HANDLE hHandle, DWORD dwMilliseconds);",
            "VirtualFree":"typedef BOOL (WINAPI *VirtualFree_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD dwFreeType);"
        }

    def imports(self) -> list[str]:
        return ['#include <windows.h>']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return f"""
{'\n'.join([value for key,value in self.typedefs.items() if key in self.apicalls ])}

FARPROC {self.name}(const char *functionName){{
    HMODULE hModule = LoadLibrary(TEXT("kernel32.dll"));
    return GetProcAddress(hModule, functionName);
}}
"""

    def resolve(self, apicalls):
        resolved = {}
        self.apicalls = apicalls
        for apicall in apicalls:
            resolved[apicall] = f'(({apicall}_t){self.name}("{apicall}"))'
        return resolved