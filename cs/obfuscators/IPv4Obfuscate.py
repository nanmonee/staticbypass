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
        self.decodedlength = len(decoded)
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + ([b"\x90"] * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
        public static byte[] {self.name}(string[] encoded)
        {{
            byte[] decoded = new byte[encoded.Length*4];
            for (int i=0; i<encoded.Length; i++){{
                string[] octets = encoded[i].Split(new [] {{'.'}});
                for (int j=0; j<4; j++){{
                    decoded[i*4+j] = (byte)Int32.Parse(octets[j]);
                }}
            }}

            return decoded[..{self.decodedlength}];
        }}
"""