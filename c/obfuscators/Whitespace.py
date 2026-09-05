import random
import string

class Whitespace:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        self.size = len(decoded)
        binary = ''.join([f'{num:08b}' for num in decoded])
        binary = binary.replace('0', ' ')
        binary = binary.replace('1', '\t')
        return binary

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char * {self.name}(const unsigned char *encoded)
{{
    int size = {self.size};
    unsigned char *out = calloc(size, sizeof(unsigned char));
    for (int i=0; i < size; i++){{
        for (int j=0; j < 8; j++){{
            if (encoded[i*8 + j] == '\\t'){{
                out[i] += 1 << (7 - j);
            }}
        }}
    }}

    return out;
}}
"""