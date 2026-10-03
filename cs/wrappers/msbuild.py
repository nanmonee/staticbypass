from string import Template

class msbuild:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['using System;',
                'using Microsoft.Build.Utilities;',
                'using Microsoft.Build.Framework;',]

    def compilerOptions(self) -> list[str]:
        return ['csproj']

    def template(self) -> str:
        return """
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Target Name="Build">
    <PayloadTask />
  </Target>
  <UsingTask
    TaskName="PayloadTask"
    TaskFactory="CodeTaskFactory"
    AssemblyFile="$(MSBuildToolsPath)\\Microsoft.Build.Tasks.v4.0.dll">
    <ParameterGroup/>
    <Task>
      <Code Type="Class" Language="cs">
<![CDATA[
{imports}

namespace ClassLibrary1
{{
    public class PayloadTask : Microsoft.Build.Utilities.Task
    {{

        {codeblocks}

        public override bool Execute()
        {{
            {template}

            return true;
        }}
    }}

}}
]]>
      </Code>
    </Task>
  </UsingTask>
</Project>
"""