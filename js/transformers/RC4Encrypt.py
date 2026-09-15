import os
from Crypto.Cipher import ARC4
from js.utils.formatters import bytes_to_js
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
        return ['import { createDecipheriv } from "node:crypto";']

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
function {self.name}(encrypted) {{
    {bytes_to_js(self.key, 'key')}
    let decrypted = new Uint8Array(encrypted.length)
    const s = new Uint8Array(256);
        for (let i = 0; i < 256; i++) {{
        s[i] = i;
    }}

    // Key Scheduling Algorithm (KSA)
    let j = 0;
    for (let i = 0; i < 256; i++) {{
        j = (j + s[i] + key[i % key.length]) % 256;
        // Swap
        const temp = s[i];
        s[i] = s[j];
        s[j] = temp;
    }}

    // Pseudo-Random Generation Algorithm (PRGA)
    let i = 0;
    j = 0;
    for (let k = 0; k < encrypted.length; k++) {{
        i = (i + 1) % 256;
        j = (j + s[i]) % 256;
        // Swap
        const temp = s[i];
        s[i] = s[j];
        s[j] = temp;

        const t = (s[i] + s[j]) % 256;
        decrypted[k] = encrypted[k] ^ s[t];
    }}

    return decrypted;
}}
"""
