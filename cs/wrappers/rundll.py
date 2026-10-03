from string import Template

class rundll:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['using System;',
                'using System.Runtime.CompilerServices;',
                'using System.Runtime.InteropServices;']

    def compilerOptions(self) -> list[str]:
        return ['dll', 'dotnet']

    def template(self) -> str:
        return """
{imports}

namespace ClassLibrary1
{{
    public class Class1
    {{

        {codeblocks}

        [UnmanagedCallersOnly(EntryPoint = "Execute", CallConvs = new[] {{ typeof(CallConvStdcall) }})]
        public static void Execute(nint hwnd, nint instance, nint commandLine, int showCommand)
        {{
            {template}
        }}
    }}

}}
"""