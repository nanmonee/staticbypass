import string
from lua.utils.typedefs import typedefs

class static:
    def __init__(self, arguments):
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        codeblock = f"""
local kernel32 = c.Library("kernel32.dll") 
local ntdll = c.Library("ntdll.dll") 
"""

        for apicall in self.apicalls:
            codeblock += f'kernel32.{apicall} = "{typedefs[apicall]}"\n'

        return codeblock

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw']:
                self.apicalls[apicall] = f'ntdll.{apicall}'
            else:
                self.apicalls[apicall] = f'kernel32.{apicall}'