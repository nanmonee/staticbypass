import random
import string
from ps1.utils.formatters import *

class embedded:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        if shellcodeType == "str":
            self.type = '[String]'
        elif shellcodeType == "bytes":
            self.type = '[Byte[]]'
        elif shellcodeType == "list":
            self.type = '[String[]]'
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_ps1'](shellcode, 'obfuscated')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}')

    def codeblock(self) -> str:
        return f"""

function {self.name} {{
    {self.shellcode}
    return $obfuscated;
}}
"""
