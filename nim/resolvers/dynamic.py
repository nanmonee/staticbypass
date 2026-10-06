import random
import string
from nim.utils.typedefs import typedefs

class dynamic:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        codeblock = ''
        for apicall in self.apicalls:
            codeblock += f"""
{typedefs[apicall]}
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
                self.apicalls[apicall] = f'(cast[{apicall}_t](GetProcAddress(LoadLibrary("ntdll.dll"), "{apicall}")))'
            else:
                self.apicalls[apicall] = f'(cast[{apicall}_t](GetProcAddress(LoadLibrary("kernel32.dll"), "{apicall}")))'