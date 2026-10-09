from string import Template

class dotnet2js:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return ['dll']

    def template(self) -> str:
        return """
{imports}

public class TestClass
{{

    {codeblocks}

    public TestClass(){{
    
        {template}
    
    }}
}}
"""