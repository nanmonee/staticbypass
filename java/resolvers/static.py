import string
from java.utils.typedefs import typedefs, ffis

class static:
    def __init__(self, arguments):
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return [ffis[apicall] for apicall in self.apicalls]
    
    def codeblocks(self) -> str:
        codeblock = """
    private static final Linker LINKER = Linker.nativeLinker();
    private static final MemoryLayout C_INT     = LINKER.canonicalLayouts().get("int");
    private static final MemoryLayout C_LONG_LONG     = LINKER.canonicalLayouts().get("long long");
    private static final MemoryLayout C_POINTER = LINKER.canonicalLayouts().get("void*");
    private static final MemoryLayout C_BOOL = LINKER.canonicalLayouts().get("bool");
    public static Arena arena = Arena.ofConfined();
    public static SymbolLookup kernel32 = SymbolLookup.libraryLookup("kernel32.dll", arena);
"""
        for apicall in self.apicalls:
            codeblock += f"""
    public static MethodHandle {apicall} = LINKER.downcallHandle(kernel32.find("{apicall}").orElseThrow(),FunctionDescriptor.of({typedefs[apicall]}));
"""
        return codeblock

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            self.apicalls[apicall] = f'{apicall}.invokeExact'