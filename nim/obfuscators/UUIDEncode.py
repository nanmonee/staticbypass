import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['import uuid4']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        self.decodedSize = len(decoded)
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes = chunk)))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded: seq[string]): seq[byte] = 
    var decoded = newSeq[byte]({self.size} * 16)
    for i in 0 ..< len(encoded):
        let uuidv4 = initUuid(encoded[i])
        let bytes = uuidv4.bytes
        for j in 0..< len(bytes):
            decoded[i*16 + j] = bytes[j]
    result = decoded[0..{self.decodedSize - 1}]
"""
