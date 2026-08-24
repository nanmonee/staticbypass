import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['sysutils']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        self.decodedLength = len(decoded)
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes_le = chunk)))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encoded: TStringArray): TBytes;
var
    i: Integer;
    decoded: TBytes;
    uuid: TGUID;
begin

    SetLength(decoded, {self.size*16});
    for i:= Low(encoded) To High(encoded) do
    begin
        uuid := TGUID.create('{{' + encoded[i] + '}}');
        Move(uuid, decoded[i*16], Sizeof(TGUID));
    end;
    Result := Copy(decoded, 0, {self.decodedLength});
end;
"""
