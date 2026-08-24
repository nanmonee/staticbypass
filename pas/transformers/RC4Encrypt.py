import os
from Crypto.Cipher import ARC4
from pas.utils.formatters import bytes_to_pas
import string
import random

class RC4Encrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encrypted: TBytes): TBytes;
var
    S: array [0 .. 255] of Byte;
    I, J, K, T, KeyLen: Integer;
    key: TBytes;
    decrypted: TBytes;
begin
    {bytes_to_pas(self.key, 'key')}
    KeyLen := Length(key);

    for I := 0 to 255 do
    S[I] := Byte(I);

    J := 0;
    for I := 0 to 255 do
    begin
        J := (J + S[I] + key[I mod KeyLen]) and $FF;
        T := S[I];
        S[I] := S[J];
        S[J] := T;
    end;

    SetLength(decrypted, Length(encrypted));
    I := 0;
    J := 0;
    for K := 0 to Length(encrypted) - 1 do
    begin
        I := (I + 1) and $FF;
        J := (J + S[I]) and $FF;
        T := S[I];
        S[I] := S[J];
        S[J] := T;
        decrypted[K] := encrypted[K] xor S[(S[I] + S[J]) and $FF];
    end;
    result := decrypted;
end;
"""
