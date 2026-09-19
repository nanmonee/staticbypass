import random
import string

class dynamic:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        if 'handle' in arguments:
            if arguments['handle'] in ['LoadLibrary', 'GetModuleHandleA']:
                self.handle = arguments['handle']
            else:
                print("Handle must be either LoadLibrary or GetModuleHandleA")
                exit(0)
        self.typedefs = {
            "VirtualAlloc":"typedef LPVOID (WINAPI *VirtualAlloc_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);",
            "CreateThread":"typedef HANDLE (WINAPI *CreateThread_t)(LPSECURITY_ATTRIBUTES lpThreadAttributes, SIZE_T dwStackSize, LPTHREAD_START_ROUTINE lpStartAddress, LPVOID lpParameter, DWORD dwCreationFlags, LPDWORD lpThreadId);",
            "HeapAlloc":"typedef LPVOID (WINAPI *HeapAlloc_t)(HANDLE hHeap, DWORD dwFlags, SIZE_T dwBytes);",
            "HeapCreate":"typedef HANDLE (WINAPI *HeapCreate_t)(DWORD flOptions, SIZE_T dwInitialSize, SIZE_T dwMaximumSize);",
            "WriteProcessMemory":"typedef BOOL (WINAPI *WriteProcessMemory_t)(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize, SIZE_T *lpNumberOfBytesWritten);",
            "CreateProcessA":"typedef BOOL (WINAPI *CreateProcessA_t)(LPCSTR lpApplicationName, LPSTR lpCommandLine, LPSECURITY_ATTRIBUTES lpProcessAttributes, LPSECURITY_ATTRIBUTES lpThreadAttributes, BOOL bInheritHandles, DWORD dwCreationFlags, LPVOID lpEnvironment, LPCSTR lpCurrentDirectory, LPSTARTUPINFOA lpStartupInfo, LPPROCESS_INFORMATION lpProcessInformation);",
            "CloseHandle":"typedef BOOL (WINAPI *CloseHandle_t)(HANDLE hObject);",
            "WaitForSingleObject":"typedef DWORD (WINAPI *WaitForSingleObject_t)(HANDLE hHandle, DWORD dwMilliseconds);",
            "VirtualFree":"typedef BOOL (WINAPI *VirtualFree_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD dwFreeType);",
            "HeapDestroy":"typedef BOOL (WINAPI *HeapDestroy_t)(HANDLE hHeap);",
            "HeapFree":"typedef BOOL (WINAPI *HeapFree_t)(HANDLE hHeap, DWORD dwFlags, LPVOID lpMem);",
            "CreateRemoteThread":"typedef HANDLE (WINAPI *CreateRemoteThread_t)(HANDLE hProcess, LPSECURITY_ATTRIBUTES lpThreadAttributes, SIZE_T dwStackSize, LPTHREAD_START_ROUTINE lpStartAddress, LPVOID lpParameters, DWORD dwCreationFlags, LPDWORD lpThreadId);",
            "VirtualAllocEx":"typedef LPVOID (WINAPI *VirtualAllocEx_t)(HANDLE hProcess, LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);",
            "QueueUserAPC":"typedef DWORD (WINAPI *QueueUserAPC_t)(PAPCFUNC pfnAPC, HANDLE hThread, ULONG_PTR dwData);",
            "ResumeThread":"typedef DWORD (WINAPI *ResumeThread_t)(HANDLE hThread);",
            "GetThreadContext":"typedef DWORD (WINAPI *GetThreadContext_t)(HANDLE hThread, LPCONTEXT lpContext);",
            "SetThreadContext":"typedef DWORD (WINAPI *SetThreadContext_t)(HANDLE hThread, LPCONTEXT lpContext);"
        }

    def imports(self) -> list[str]:
        return ['#include <windows.h>']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return f"""
{'\n'.join([value for key,value in self.typedefs.items() if key in self.apicalls ])}

typedef struct {{
    {'\n\t'.join([f'{x}_t {x}_resolved;' for x in self.apicalls ])}
}} Resolver;

Resolver resolver;

void {self.name}(void) __attribute__((constructor));

void {self.name}(){{
    HMODULE hModule = {self.handle}(TEXT("kernel32.dll"));
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)GetProcAddress(hModule, "{x}");' for x in self.apicalls])};
}}
"""

    def resolve(self, apicalls):
        resolved = {}
        self.apicalls = apicalls
        for apicall in apicalls:
            resolved[apicall] = f'resolver.{apicall}_resolved'
        return resolved