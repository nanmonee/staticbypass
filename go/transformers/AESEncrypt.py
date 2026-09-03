import os
from go.utils.formatters import bytes_to_go
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
        return ['crypto/aes', 
                'crypto/cipher']

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
func {self.name}(ciphertext []byte) []byte {{
    {bytes_to_go(self.key, 'key')}
    {bytes_to_go(self.iv, 'iv')}
    
	block, _ := aes.NewCipher(key)

	mode := cipher.NewCBCDecrypter(block, iv)
	mode.CryptBlocks(ciphertext, ciphertext)

	length := len(ciphertext)
	unpadding := int(ciphertext[length-1])
	return ciphertext[:length-unpadding]
}}
"""