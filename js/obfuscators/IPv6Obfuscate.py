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
        self.decodedlength = len(decoded)
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
function {self.name}(addresses) {{
    let decoded = new Uint8Array(addresses.length * 16); 
    for (let i = 0; i < addresses.length; i++) {{
        let hextets = addresses[i].split(':');
        for (let j = 0; j < hextets.length; j++){{
            let parsed = parseInt(hextets[j], 16)
            decoded[i*16 + j*2] = parsed >> 8;
            decoded[i*16 + j*2 + 1] = parsed % 256;
        }}
    }}
    return decoded.slice(0, {self.decodedlength});
}}
"""