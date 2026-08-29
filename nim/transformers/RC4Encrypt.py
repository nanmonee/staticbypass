import os
from Crypto.Cipher import ARC4
from nim.utils.formatters import bytes_to_nim
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
        return ['import strutils']

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
func {self.name}(encrypted: seq[byte]): seq[byte] =

    {bytes_to_nim(self.key, 'key')}

    var s: array[256, int]
    for i in 0..255:
        s[i] = i

    var j = 0
    for i in 0..255:
        j = (j + s[i] + int(key[i mod key.len])) mod 256
        swap(s[i], s[j])

    result = newSeq[byte](encrypted.len)
    var i = 0
    j = 0
    for idx in 0..<encrypted.len:
        i = (i + 1) mod 256
        j = (j + s[i]) mod 256
        swap(s[i], s[j])
        let t = (s[i] + s[j]) mod 256
        let k = s[t]
        result[idx] = encrypted[idx] xor byte(k)
"""
