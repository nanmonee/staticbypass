typedefs = {
    "VirtualAlloc":"type VirtualAlloc_t = proc(lpAddress: pointer, dwSize: SIZE_T, flAllocationType: DWORD, flProtect: DWORD): pointer {.stdcall.}",
    "CreateThread":"type CreateThread_t = proc(lpThreadAttributes: LPSECURITY_ATTRIBUTES, dwSize: SIZE_T, lpStartAddress: LPTHREAD_START_ROUTINE, lpParameter: pointer, dwCreationFlags: DWORD, lpThreadId: pointer): HANDLE {.stdcall.}",
    "WaitForSingleObject":"type WaitForSingleObject_t = proc(hHandle: HANDLE, dwMilliseconds: DWORD): DWORD {.stdcall.}",
    "CreateProcessA":"type CreateProcessA_t = proc(lpApplicationName: LPCSTR, lpCommandLine: LPSTR, lpProcessAttributes: LPSECURITY_ATTRIBUTES, lpThreadAttributes: LPSECURITY_ATTRIBUTES, bInheritHandles: BOOL, dwCreationFlags: DWORD, lpEnvironment: pointer, lpCurrentDirectory: LPCSTR, lpStartupInfo: LPSTARTUPINFOA, lpProcessInformation: LPPROCESS_INFORMATION): bool {.stdcall.}",
    "VirtualAllocEx":"type VirtualAllocEx_t = proc(hProcess: HANDLE, lpAddress: pointer, dwSize: SIZE_T, flAllocationType: DWORD, flProtect: DWORD): pointer {.stdcall.}",
    "WriteProcessMemory":"type WriteProcessMemory_t = proc(hProcess: HANDLE, lpBaseAddress: pointer, lpBuffer: pointer, nSize: SIZE_T, lpNumberOfBytesWritten: pointer): bool {.stdcall.}",
    "CreateRemoteThread":"type CreateRemoteThread_t = proc(hProcess: HANDLE, lpThreadAttributes: LPSECURITY_ATTRIBUTES, dwStackSize: SIZE_T, lpStartAddress: LPTHREAD_START_ROUTINE, lpParameter: pointer, dwCreationFlags: DWORD, lpThreadId: pointer): pointer {.stdcall.}",
    "CloseHandle":"type CloseHandle_t = proc(hObject: HANDLE): bool {.stdcall.}",
    "VirtualProtect":"type VirtualProtect_t = proc(lpAddress: pointer, dwSize: SIZE_T, flAllocationType: DWORD, lpflOldProtect: PDWORD): pointer {.stdcall.}",
    "VirtualProtectEx":"type VirtualProtectEx_t = proc(hProcess: HANDLE, lpAddress: pointer, dwSize: SIZE_T, flAllocationType: DWORD, lpflOldProtect: PDWORD): pointer {.stdcall.}",
    "NtAllocateVirtualMemory":"type NtAllocateVirtualMemory_t = proc(ProcessHandle: HANDLE, BaseAddress: pointer, ZeroBits: pointer, RegionSize: pointer, AllocationType: ULONG, Protect: ULONG): NTSTATUS {.stdcall.}",
    "NtWriteVirtualMemory":"type NtWriteVirtualMemory_t = proc(ProcessHandle: HANDLE, BaseAddress: pointer, Buffer: pointer, NumberOfBytesToWrite: uint64, NumberOfBytesWritten: pointer): NTSTATUS {.stdcall.}",
    "NtCreateThreadEx":"type NtCreateThreadEx_t = proc(ThreadHandle: pointer, DesiredAccess: DWORD, ObjectAttributes: pointer, ProcessHandle: HANDLE, StartRoutine: pointer, Argument: pointer, CreateFlags: ULONG, ZeroBits: uint64, StackSize: uint64, MaximumStackSize: uint64, AttributeList: pointer): NTSTATUS {.stdcall.}",
    "NtProtectVirtualMemory":"type NtProtectVirtualMemory_t = proc(ProcessHandle: HANDLE, BaseAddress: pointer, RegionSize: pointer, NewProtection: ULONG, OldProtection: pointer): NTSTATUS {.stdcall.}",
    "NtWaitForSingleObject":"type NtWaitForSingleObject_t = proc(Handle: HANDLE, Alertable: BOOLEAN, Timeout: pointer): NTSTATUS {.stdcall.}",
}

bindings = {
    "NtAllocateVirtualMemory":'proc NtAllocateVirtualMemory(ProcessHandle: HANDLE, BaseAddress: pointer, ZeroBits: pointer, RegionSize: pointer, AllocationType: ULONG, Protect: ULONG): NTSTATUS {.stdcall, dynlib: "ntdll", importc.}',
    "NtWriteVirtualMemory":'proc NtWriteVirtualMemory(ProcessHandle: HANDLE, BaseAddress: pointer, Buffer: pointer, NumberOfBytesToWrite: uint64, NumberOfBytesWritten: pointer): NTSTATUS {.stdcall, dynlib: "ntdll", importc.}',
    "NtCreateThreadEx":'proc NtCreateThreadEx(ThreadHandle: pointer, DesiredAccess: DWORD, ObjectAttributes: pointer, ProcessHandle: HANDLE, StartRoutine: pointer, Argument: pointer, CreateFlags: ULONG, ZeroBits: uint64, StackSize: uint64, MaximumStackSize: uint64, AttributeList: pointer): NTSTATUS {.stdcall, dynlib: "ntdll", importc.}',
    "NtProtectVirtualMemory":'proc NtProtectVirtualMemory(ProcessHandle: HANDLE, BaseAddress: pointer, RegionSize: pointer, NewProtection: ULONG, OldProtection: pointer): NTSTATUS {.stdcall, dynlib: "ntdll", importc.}',
    "NtWaitForSingleObject":'proc NtWaitForSingleObject(Handle: HANDLE, Alertable: BOOLEAN, Timeout: pointer): NTSTATUS {.stdcall, dynlib: "ntdll", importc.}',
}