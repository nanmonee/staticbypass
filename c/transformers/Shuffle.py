import string
import random

class Shuffle:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.state = random.randint(0, 2**32)

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.plaintextSize = len(plaintext)
        encoded = list(plaintext)
        next = self.state
        random = 0
        for i in range(len(plaintext) - 1, 0, -1):
            next = (next * 1664525 +  1013904223) % 2**32
            random = ((next >> 16) % 32768) % i
            temp = encoded[random]
            encoded[random] = encoded[i]
            encoded[i] = temp

        self.state = next % 2**32
        return bytes(encoded)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char *{self.name}(const unsigned char *encoded)
{{
    int len = {self.plaintextSize};
    unsigned char * decoded = malloc(len);
    memcpy(decoded, encoded, len);
    int random = 0;
    int temp = 0;

    unsigned int prev = {self.state};
    for (int i = 1; i < len; i++) {{
        int random = ((prev >> 16) % 32768) % i;
        prev = (prev - 1013904223) * 4276115653; 

        unsigned char temp = decoded[random];
        decoded[random] = decoded[i];
        decoded[i] = temp;
    }}
    
    return decoded;
}}
"""