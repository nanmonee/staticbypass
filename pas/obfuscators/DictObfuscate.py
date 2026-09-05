import random
import string
from pas.utils.formatters import dict_to_pas
import time

class DictObfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
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
        return ["fgl"]

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
function {self.name}(encoded: String): TBytes;
type 
    TStringIntMap = TFPGMap<String, Integer>;
var
    i: Integer;
    dictionary: TStringIntMap;
    words: TStringArray;
begin
    Result := nil;
    {dict_to_pas(self.dictdecode, 'dictionary')}
    SetLength(Result, {self.size});
    words := encoded.Split([' ']);
    for i:= Low(words) To High(words) do
    begin
        Result[i] := dictionary[words[i]];
    end;
end;
"""