typedefs = {
    "VirtualAlloc":"type VirtualAlloc_t = proc(lpAddress: pointer, dwSize: SIZE_T, flAllocationType: DWORD, flProtect: DWORD): pointer {.stdcall.}",
    "CreateThread":"type CreateThread_t = proc(lpThreadAttributes: LPSECURITY_ATTRIBUTES, dwSize: SIZE_T, lpStartAddress: LPTHREAD_START_ROUTINE, lpParameter: pointer, dwCreationFlags: DWORD, lpThreadId: pointer): pointer {.stdcall.}",
    "WaitForSingleObject":"type WaitForSingleObject_t = proc(hHandle: HANDLE, dwMilliseconds: DWORD): DWORD {.stdcall.}",
    "CreateProcessA":"type CreateProcessA_t = proc(lpApplicationName: LPCSTR, lpCommandLine: LPSTR, lpProcessAttributes: LPSECURITY_ATTRIBUTES, lpThreadAttributes: LPSECURITY_ATTRIBUTES, bInheritHandles: BOOL, dwCreationFlags: DWORD, lpEnvironment: pointer, lpCurrentDirectory: LPCSTR, lpStartupInfo: LPSTARTUPINFOA, lpProcessInformation: LPPROCESS_INFORMATION): bool {.stdcall.}",
    "VirtualAllocEx":"type VirtualAllocEx_t = proc(hProcess: HANDLE, lpAddress: pointer, dwSize: SIZE_T, flAllocationType: DWORD, flProtect: DWORD): pointer {.stdcall.}",
    "WriteProcessMemory":"type WriteProcessMemory_t = proc(hProcess: HANDLE, lpBaseAddress: pointer, lpBuffer: pointer, nSize: SIZE_T, lpNumberOfBytesWritten: pointer): bool {.stdcall.}",
    "CreateRemoteThread":"type CreateRemoteThread_t = proc(hProcess: HANDLE, lpThreadAttributes: LPSECURITY_ATTRIBUTES, dwStackSize: SIZE_T, lpStartAddress: LPTHREAD_START_ROUTINE, lpParameter: pointer, dwCreationFlags: DWORD, lpThreadId: pointer): pointer {.stdcall.}",
    "CloseHandle":"type CloseHandle_t = proc(hObject: HANDLE): bool {.stdcall.}"
}