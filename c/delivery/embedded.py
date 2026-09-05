import random
import string
from c.utils.formatters import *

class embedded:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        if 'section' in arguments:
            const = not (arguments['section'] == 'data')
        else:
            const = True
        if shellcodeType == "str":
            self.type = f'{'const' if const else ''} unsigned char *'
        elif shellcodeType == "bytes":
            self.type = f'{'const' if const else ''} unsigned char *'
        elif shellcodeType == "list":
            self.type = f'{'const' if const else ''} unsigned char **'
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, 'obfuscated', const)

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        return f"""
{self.type} {self.name}() {{
    {self.shellcode}
    return obfuscated;
}}
"""
