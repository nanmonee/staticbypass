import random
import string
from c.utils.formatters import *

class embedded:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.type = type(shellcode).__name__
        self.section = 'rdata'
        if 'section' in arguments:
            if arguments['section'] not in ['data', 'rdata', 'text']:
                print('Section must be either data, rdata, or text')
                exit(0)
            self.section = arguments['section']
            if self.section == 'text':
                self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, self.name, True)
            else:
                self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, 'obfuscated', self.section == 'rdata')
        else:
            self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, 'obfuscated', self.section == 'rdata')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return ['-Wincompatible-pointer-types']

    def transformer(self, shellcodestring: str) -> str:
        if self.section == 'text':
            return shellcodestring.format(shellcode=self.name)
        else:
            return shellcodestring.format(shellcode=f'(const unsigned char **){self.name}()')

    def codeblock(self) -> str:
        if self.section == 'text':
            return f"""
#pragma section(".text$payload", read, execute)
{self.shellcode}
"""

        if self.type == 'bytes':
            return f"""
{'const' if self.section == 'rdata' else ''} unsigned char *{self.name}() {{
    {self.shellcode}
    return obfuscated;
}}
"""

        elif self.type == 'str':
            return f"""
{'const' if self.section == 'rdata' else ''} unsigned char * {self.name}() {{
    {self.shellcode}
    return obfuscated;
}}
"""

        else:
            return f"""
{'const' if self.section == 'rdata' else ''} unsigned char ** {self.name}() {{
    {self.shellcode}
    return obfuscated;
}}
"""