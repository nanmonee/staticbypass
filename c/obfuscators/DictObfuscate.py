import random
import string
from c.utils.formatters import *
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
        return ["#include <string.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-I/usr/include/uthash']

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
        wordArray = list_to_c([self.dictencode[i] for i in range(0, 256)], 'wordArray')
        return f"""
static struct {{ 
    char *word; 
    int value; 
}} dictionary[256];

static unsigned idx(char *word) {{
    unsigned hash = 5381;
    for (char *p = word; *p; p++) {{
        hash = hash * 33 + *p;
    }}
    for (hash %= 256; dictionary[hash].word && strcmp(dictionary[hash].word, word); hash = (hash + 1) % 256);
    return h;
}}

void set(char *word, int value) {{ 
    unsigned i = idx(word); 
    dictionary[i].word = word; 
    dictionary[i].value = value; 
}}

int get(char *word) {{ 
    unsigned i = idx(word); 
    return dictionary[i].word ? dictionary[i].value : 0; 
}}

unsigned char * {self.name}(const unsigned char* encoded)
{{
    int size = {self.size};
    unsigned char *buffer = strdup(encoded);
    unsigned char * out = malloc(size);
    int i = 0;
    {dict_to_c(self.dictdecode, 'dictionary')}
    char * currWord = strtok(buffer, " ");
    while (currWord != NULL){{
        out[i] = get(currWord);
        i++;        
        currWord = strtok(NULL, " ");
    }}

    return out;
}}
"""