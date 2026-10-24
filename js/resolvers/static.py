import string
from js.utils.typedefs import typedefs

class static:
    def __init__(self, arguments):
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        apicalls = ','
        return f"""
const kernel32Path = "C:\\\\Windows\\\\System32\\\\kernel32.dll";
const kernel32 = Deno.dlopen(kernel32Path, {{
    {',\n\t'.join([typedefs[apicall] for apicall in self.apicalls])}
}})
"""

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            self.apicalls[apicall] = f'kernel32.symbols.{apicall}'