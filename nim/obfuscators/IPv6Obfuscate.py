import random
import string

class IPv6Obfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['import strutils']

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
            encoded.append(':'.join([ f'{chunk[n]:02x}{chunk[n+1]:02x}' for n in range(0, 16, 2)]))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded: seq[string]): seq[byte] = 
    var decoded = newSeq[byte]({self.size} * 16)
    for i in 0 ..< len(encoded):
        let address = encoded[i]
        let hextets = address.split(':')
        for j in 0 ..< len(hextets):
            let converted = parseHexInt(hextets[j])
            decoded[i*16 + j*2] = byte(converted shr 8)
            decoded[i*16 + j*2 + 1] = byte(converted and 255)

    result = decoded[0..{self.decodedSize - 1}]
"""