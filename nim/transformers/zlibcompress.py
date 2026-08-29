import string
import random
import zlib

class zlibcompress:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['import zippy']

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.uncompressedLength = len(plaintext)
        compressed = zlib.compress(plaintext)
        self.compressedLength = len(compressed)
        return compressed

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(compressed: seq[byte]): seq[byte] = 
    let decompressed = uncompress(compressed, dataFormat = dfZlib) 
    result = decompressed
"""
