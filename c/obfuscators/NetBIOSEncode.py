import random
import string

class NetBIOSEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        encoded = ''
        for i in range(0, len(decoded)):
            encoded += chr((decoded[i] >> 4) + ord('A'))
            encoded += chr((decoded[i] & 0xF) + ord('A'))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char* {self.name}(const unsigned char* netbios) {{
    int length = strlen(netbios);
    unsigned char *decoded = malloc(length/2);
    for (int i = 0; i < length/2; i++){{
        decoded[i] = (netbios[i*2] - (int)'A') << 4;
        decoded[i] += (netbios[i*2 + 1] - (int)'A') & 0xF;
    }}
    return decoded;
}}
"""
            