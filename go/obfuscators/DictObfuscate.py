import random
import string
from go.utils.formatters import dict_to_go
import time

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
        randomNumbers = self.rng.sample(range(0, len(wordlist)), 256)
        for i in range(0, 256):
            word = wordlist[randomNumbers[i]].strip()
            self.dictencode[i] = word
            self.dictdecode[word] = i

    def imports(self) -> list[str]:
        return ['strings']

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        self.size = len(decoded)
        encoded = ''
        for i in range(0, len(decoded) - 1):
            encoded += self.dictencode[decoded[i]] + ' '
        encoded += self.dictencode[decoded[-1]]
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(encoded string) []byte {{
    {dict_to_go(self.dictdecode, 'dictionary')}
    decoded := make([]byte, {self.size})
    words := strings.Split(encoded, " ")
    for i, word := range words {{
        decoded[i] = byte(dictionary[word])
    }}
    return decoded
}}
"""