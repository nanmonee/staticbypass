import base64
import random
import string

class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""

function CryptStringToBinaryA(pszString: PAnsiChar; cchString: DWORD; dwFlags: DWORD; pbBinary: PByte; var pcbBinary: DWORD; pdwSkip: PDWORD; pdwFlags: PDWORD): BOOL; stdcall; external 'crypt32.dll' name 'CryptStringToBinaryA';

function {self.name}(encoded: String): TBytes;
var
    Src: PAnsiChar;
    SrcLen, BinLen: DWORD;

begin
    Result := nil;
    SrcLen := Length(encoded);
    BinLen := 0;

    if not CryptStringToBinaryA(PAnsiChar(encoded), SrcLen, $00000001, nil, BinLen, nil, nil) then RaiseLastOSError;

    SetLength(Result, BinLen);

    if not CryptStringToBinaryA(PAnsiChar(encoded), SrcLen, $00000001, PByte(@Result[0]), BinLen, nil, nil) then RaiseLastOSError;
end;
"""