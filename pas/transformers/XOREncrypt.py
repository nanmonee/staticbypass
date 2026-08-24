import random
import string
from pas.utils.formatters import bytes_to_pas
import os

class XOREncrypt:

    def __init__(self, arguments: dict) -> None:
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []
    
    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encrypted: TBytes): TBytes;
var
    key: TBytes;
    i: Integer;
    decrypted: TBytes;

begin
    {bytes_to_pas(self.key, 'key')}
    SetLength(decrypted, Length(encrypted));
    for i := 0 to Length(encrypted) - 1 do
    begin
        decrypted[i] := byte(Ord(encrypted[i]) xor Ord(key[i mod Length(key)]))
    end;
    Result := decrypted;
end;
"""