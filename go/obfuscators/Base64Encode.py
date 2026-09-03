import base64
import random
import string

class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['encoding/base64']

    def compilerOptions(self) -> list[str]:
        return ["encoding/base64"]

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded string) []byte {{
	decoded, _ := base64.StdEncoding.DecodeString(encoded)
    return decoded
}}
"""
            