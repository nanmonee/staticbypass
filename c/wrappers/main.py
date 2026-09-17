class main:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['#include <tchar.h>']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}

{codeblocks}

int app_main() {{
    {template}
    return 0;
}}

int main(void)  {{
    return app_main(); 
}}

int wmain(void) {{
    return app_main(); 
}}
"""