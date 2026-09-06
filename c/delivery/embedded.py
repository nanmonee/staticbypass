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
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, self.name, self.section != 'data')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        if self.type == 'list':
            return shellcodestring.format(shellcode=f'(const unsigned char **){self.name}')
        elif self.type == 'bytes':
            return shellcodestring.format(shellcode=f'(unsigned char *){self.name}')
        return shellcodestring.format(shellcode=self.name)

    def codeblock(self) -> str:
        if self.section == 'text':
            return f"""
#pragma section(".text${self.name}", read, execute)
__attribute__((section(".text${self.name}"))) {self.shellcode}
"""

        return f"""
{self.shellcode}
"""