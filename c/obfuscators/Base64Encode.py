import base64
import random
import string

class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ["#include <stdio.h>", 
                "#include <wincrypt.h>", 
                "#include <stdlib.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-lcrypt32']

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char* {self.name}(const unsigned char* base64Str) {{

    // 1. Calculate the required buffer size
    DWORD binaryLen = 0;
    CryptStringToBinaryA(base64Str, 0, CRYPT_STRING_BASE64, 
                         NULL, &binaryLen, NULL, NULL);

    if (binaryLen == 0) return NULL;

    // 2. Allocate memory + 1 byte for null terminator
    char* decodedData = (char*)malloc(binaryLen + 1);
    if (decodedData == NULL) return NULL;

    // 3. Perform the actual decoding
    if (!CryptStringToBinaryA(base64Str, 0, CRYPT_STRING_BASE64, 
                             (BYTE*)decodedData, &binaryLen, NULL, NULL)) {{
        free(decodedData);
        return NULL;
    }}

    // 4. Null-terminate as a C-string
    decodedData[binaryLen] = '\\0';

    return decodedData;
}}
"""
            