import random
import string
from nim.utils.formatters import bytes_to_nim
import os

class XOREncrypt:

    def __init__(self, arguments: dict) -> None:
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []
    
    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encrypted: seq[byte]): seq[byte] = 
    {bytes_to_nim(self.key, 'key')}
    var plaintext = encrypted

    for i in 0 ..< len(plaintext):
        plaintext[i] = plaintext[i] xor key[i mod len(key)]

    result = plaintext
"""