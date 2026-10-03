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

namespace ClassLibrary1
{{
    public class Class1
    {{

        {codeblocks}

        static void Main(string[] args)
        {{
            {template}
        }}
    }}

}}



"""