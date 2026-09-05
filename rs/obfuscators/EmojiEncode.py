import random
import string

class EmojiEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        encoded = ""
        self.size = len(decoded)
        print(decoded)
        for i in range(0, len(decoded)):
            encoded += chr(0x1f400 + decoded[i])
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encoded: &str) -> Vec<u8> {{
    let mut decoded = vec![0; {self.size}];
    for (i, character) in encoded.chars().enumerate() {{
        decoded[i] = (character as u32 & 255) as u8;
    }}
    decoded
}}
"""
