class rundll:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>",
                "#include <stdlib.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-luser32',
                '-shared']

    def template(self) -> str:
        return """
{imports}

{codeblocks}

int executecode(){{
    
    {template}
}}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {{
    if (fdwReason == DLL_PROCESS_ATTACH) {{
        executecode();
    }}
    return TRUE;
}}

__attribute__((dllexport)) void CALLBACK Dummy(HWND hwnd, HINSTANCE h, LPSTR c, int n) {{}}
"""