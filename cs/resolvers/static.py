import string
from cs.utils.typedefs import typedefs

class static:
    def __init__(self, arguments):
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw']:
                codeblock += f"""
        [DllImport("ntdll.dll", CallingConvention = CallingConvention.StdCall)]
        private static extern {typedefs[apicall]}
"""
            else:
                codeblock += f"""
        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
        private static extern {typedefs[apicall]}
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
            self.apicalls[apicall] = f'{apicall}'