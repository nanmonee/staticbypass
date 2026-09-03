import random
import string

class EmojiEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

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
        public static byte[] {name}(string encoded)
        {{
            byte[] decoded = new byte[encoded.Length/2];
            for (int i=0; i< encoded.Length/2; i++ ){{
                decoded[i] = (byte)(char.ConvertToUtf32(encoded.Substring(i*2, 2), 0) & 255);
            }}
            return decoded;
        }}
""".format(name = self.name)