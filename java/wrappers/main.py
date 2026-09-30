from string import Template

class main:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}

public class MessageBoxDemo {{

    {codeblocks}

    public static void main(String[] args) throws Throwable {{
        {template}
    }}
}}
"""