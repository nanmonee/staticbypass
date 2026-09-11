from string import Template

class rundll:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}

{codeblocks}

#[no_mangle]
pub extern "C" fn runcode() {{

    {template}
    
}} 
"""