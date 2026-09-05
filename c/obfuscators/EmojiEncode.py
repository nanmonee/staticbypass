import random
import string

class EmojiEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ["#include <stdint.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        encoded = ""
        for i in range(0, len(decoded)):
            encoded += chr(0x1f400 + decoded[i])
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char * {self.name}(const unsigned char *encoded)
{{
    int length = strlen(encoded);
    unsigned char *out = malloc(length/4);
    int hexcode;
    for (int i=0; i< length/4; i++ ){{
        unsigned char s[4];
        memcpy(s, &encoded[i*4], 4);
        hexcode = ((uint32_t)(s[0] & 0x07) << 18) | ((uint32_t)(s[1] & 0x3F) << 12) | ((uint32_t)(s[2] & 0x3F) << 6) |  (s[3] & 0x3F);
        out[i] = hexcode & 255;
    }}
    return out;
}}
"""
