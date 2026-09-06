import random
import string

class username:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.allow = ''
        self.deny = ''
        if 'allow' in arguments:
            self.allow = arguments['allow']
        elif 'deny' in arguments:
            self.deny = arguments['deny']
        else:
            self.deny = 'JohnDoe'

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return f'{self.name}();\n\t' + shellcodestring

    def codeblock(self) -> str:
        if self.allow:
            allow = f'if (username != "{self.allow}") {{ Environment.Exit(0); }};'
        else:
            allow = ''
        if self.deny:
            deny = f'if (username == "{self.deny}") {{ Environment.Exit(0); }};'
        else:
            deny = ''

        return f"""
        public static void {self.name}()
        {{
            string username = Environment.UserName;

            {allow}
            {deny}
        }}
"""
