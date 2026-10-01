import random
import string
from java.utils.formatters import bytes_to_java
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
    public static byte[] {self.name}(byte[] ciphertext) {{
        {bytes_to_java(self.key, 'key')}
        byte[] decrypted = new byte[ciphertext.length];
        for (int i=0; i<ciphertext.length; i++){{
            decrypted[i] = (byte) (ciphertext[i] ^ key[i % key.length]);
        }}
        return decrypted;
    }}
"""