import random
import string
from c.utils.typedefs import typedefs

class dynamic:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        if 'handle' in arguments:
            if arguments['handle'] in ['LoadLibrary', 'GetModuleHandleA']:
                self.handle = arguments['handle']
            else:
                print("Handle must be either LoadLibrary or GetModuleHandleA")
                exit(0)
        self.typedefs = typedefs

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        kernel32 = []
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw', 'Rt']:
                ntdll.append(apicall)
            else:
                kernel32.append(apicall)

        codeblock += f"""

{'\n'.join([value for key,value in self.typedefs.items() if key in self.apicalls ])}

typedef struct {{
    {'\n\t'.join([f'{x}_t {x}_resolved;' for x in self.apicalls ])}
}} Resolver;

Resolver resolver;

void {self.name}(void) __attribute__((constructor));

void {self.name}(){{
"""
        if len(kernel32) > 0:
            codeblock += f"""
    HMODULE kernel32Module = {self.handle}(TEXT("kernel32.dll"));
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)GetProcAddress(kernel32Module, "{x}");' for x in kernel32])};
"""

        if len(ntdll) > 0:
            codeblock += f"""
    HMODULE ntdllModule = {self.handle}(TEXT("ntdll.dll"));
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)GetProcAddress(ntdllModule, "{x}");' for x in ntdll])};
"""

        codeblock += f"""
}}
"""
        return codeblock

    def resolve(self, apicalls):
        resolved = {}
        self.apicalls = apicalls
        for apicall in apicalls:
            resolved[apicall] = f'resolver.{apicall}_resolved'
        return resolved