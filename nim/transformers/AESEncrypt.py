import os
from nim.utils.formatters import bytes_to_nim
from Crypto.Cipher import AES
from Crypto.Util import Padding
import string
import random

class AESEncrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(32)
        if 'iv' in arguments:
            self.iv = arguments['iv'].encode()
        else:
            self.iv = os.urandom(16)

    def imports(self) -> list[str]:
        return ["import nimcrypto"]

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.plaintextSize = len(plaintext)
        encrypted = cipher.encrypt(Padding.pad(plaintext, 16, style='pkcs7'))
        self.ciphertextSize = len(encrypted)
        return encrypted

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encrypted: seq[byte]): seq[byte] = 

    var ctx: CBC[aes256]
    var decrypted = newSeq[byte](len(encrypted))
    
    {bytes_to_nim(self.key, 'key')}
    {bytes_to_nim(self.iv, 'iv')}
    ctx.init(key, iv)
    ctx.decrypt(encrypted, decrypted)
    ctx.clear()
    
    result = decrypted[0..{self.plaintextSize - 1}]
"""