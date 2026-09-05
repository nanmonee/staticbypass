import random
import string

class IPv4Obfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = len(decoded)
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + (b"\x90" * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encoded: &Vec<String>) -> Vec<u8> {{
    let mut decoded = vec![0; {self.size}];
    for (i, ip) in encoded.iter().enumerate(){{
        let octets: Vec<&str> = ip.split('.').collect();
        for (j, octet) in octets.iter().enumerate(){{
            if i*4+j >= {self.size}{{
                return decoded.to_vec()
            }}
            decoded[i*4 + j] =  octet.parse::<u8>().unwrap();
        }}
    }}
    decoded
}}
"""