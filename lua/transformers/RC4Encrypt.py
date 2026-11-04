import os
from Crypto.Cipher import ARC4
from lua.utils.formatters import bytes_to_lua
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
        return ['local crypto = require "crypto"']

    def compilerOptions(self) -> list[str]:
        return ['-lcrypto']

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(ciphertext) 
    {bytes_to_lua(self.key, 'key')}
    local S = {{}}
    for i=0, 255, 1 do
        S[i] = i
    end

    local j = 0
    for i=0, 255, 1 do
        j = (j + S[i] + key[i % 16 + 1]) % 256
        tmp = S[i]
        S[i] = S[j]
        S[j] = tmp
    end

    local i = 0
    local j = 0
    local t = 0
    for s=0, #ciphertext - 1, 1 do
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        tmp = S[i]
        S[i] = S[j]
        S[j] = tmp
        t = (S[i] + S[j]) % 256
        ciphertext[s + 1] = S[t] ~ ciphertext[s + 1]
    end
    return ciphertext    
end
"""
