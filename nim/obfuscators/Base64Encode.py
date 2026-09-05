import base64
import random
import string

class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['import std/base64']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded: string): seq[byte] = 
    var decoded = decode(encoded)
    result = cast[seq[byte]](decoded)
"""
            