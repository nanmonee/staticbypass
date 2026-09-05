import random
import string

class EmojiEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['Character']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        encoded = ""
        self.size = len(decoded)
        for i in range(0, len(decoded)):
            encoded += chr(0x1f400 + decoded[i])
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encoded: UnicodeString): TBytes;
var
    decoded: TBytes;
    i: Integer;
    emoji: UCS4Char;
    length: Integer;
begin
    SetLength(decoded, {self.size});
    i := Low(encoded);
    while i <= High(encoded) do
    begin
        emoji := TCharacter.ConvertToUtf32(encoded, i, length);
        decoded[Trunc(i / 2)] := Integer(emoji) and 255;
        Inc(i, 2);
    end;
    Result := decoded;
end;
"""
