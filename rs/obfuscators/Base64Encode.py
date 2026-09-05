import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ["use base64::prelude::*;"]

    def compilerOptions(self) -> list[str]:
        return ['base64 = "0.22.1"']

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encoded: &str) -> Vec<u8> {{
    BASE64_STANDARD.decode(encoded).unwrap()
}}
"""