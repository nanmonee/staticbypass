import random
import string
from c.utils.typedefs import typedefs
class static:
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.handle = 'LoadLibrary'
        if 'handle' in arguments:
            if arguments['handle'] in ['LoadLibrary', 'GetModuleHandleA']:
                self.handle = arguments['handle']
            else:
                print("Handle must be either LoadLibrary or GetModuleHandleA")
        self.typedefs = typedefs
        self.apicalls = {}

    def imports(self) -> list[str]:
        return ['#include <windows.h>',
                '#include "spawnandinject.h"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        ntdll = []
        codeblock = ''
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw', 'Rt']:
                ntdll.append(apicall)

        if len(ntdll) > 0:
            codeblock += f"""

{'\n'.join([value for key,value in self.typedefs.items() if key in ntdll ])}

typedef struct {{
    {'\n\t'.join([f'{x}_t {x}_resolved;' for x in ntdll ])}
}} Resolver;

NTSTATUS status;

Resolver resolver;

void {self.name}(void) __attribute__((constructor));

void {self.name}(){{
"""
        if len(ntdll) > 0:
            codeblock += f"""
    HMODULE ntdllHandle = {self.handle}(TEXT("ntdll.dll"));
    {'\n\t'.join([f'resolver.{x}_resolved = ({x}_t)GetProcAddress(ntdllHandle, "{x}");' for x in ntdll])};
"""

            codeblock += f"""
}}
"""
        return codeblock

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            if apicall[0:2] in ['Nt', 'Zw', 'Rt']:
                self.apicalls[apicall] = f'status = resolver.{apicall}_resolved'
            else:
                self.apicalls[apicall] = apicall
