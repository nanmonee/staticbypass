import random
import string
from nim.utils.formatters import *

class embedded:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.type = type(shellcode).__name__
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_nim'](shellcode, 'obfuscated')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:

        if self.type == 'bytes':
            return f"""
proc {self.name}(): seq[byte] =
    {self.shellcode}
    result = obfuscated
"""
        elif self.type == 'str':
            return f"""
proc {self.name}(): string =
    {self.shellcode}
    result = obfuscated
"""
        elif self.type == 'list':
            return f"""
proc {self.name}(): seq[string] =
    {self.shellcode}
    result = obfuscated
"""