import random
import string

class counter:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))


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
    int counter = 0;
    int i = 0;
    for (i = 0; i < 150000000000ULL; i++) {{
        counter++;
    }}

    if (counter == 150000000000ULL){{
        return;
    }}
}}
"""