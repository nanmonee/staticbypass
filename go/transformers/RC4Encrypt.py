import os
from Crypto.Cipher import ARC4
from go.utils.formatters import bytes_to_go
import string
import random

class RC4Encrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def imports(self) -> list[str]:
        return ['crypto/rc4']

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(ciphertext []byte) []byte {{
    {bytes_to_go(self.key, 'key')}
    
	cipher, _ := rc4.NewCipher(key)

	plaintext := make([]byte, len(ciphertext))
	cipher.XORKeyStream(plaintext, ciphertext)
    return plaintext
}}
"""
