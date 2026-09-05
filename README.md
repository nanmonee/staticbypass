# StaticBypass - Template-based, modular, multi-language, shellcode obfuscator and compiler

## Features
- Takes in a raw shellcode or executable file, applies encryptors and obfuscators, formats it, places it into a template, and compiles it
- Supports C, C#, PowerShell, VBA, Rust, Go, Pascal, and Nim
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

# Spawn a process and inject into it using VM-based obfuscation
python3 staticbypass.py -s ~/shellcode.bin -b mkpivm64 -e IPv4Obfuscate -t spawnandinject -l c -a strip

# Donut an executable then AESEncrypt it and UUIDEncode it and compile it with rust
python3 staticbypass.py -s mimikatz.exe -b donut -e AESEncrypt -t shellcoderunner -l rust

# Generate a vba script that uses writes text into the word document
python3 staticbypass.py -s ~/shellcode.bin -e DictObfuscate -a embedtext -t processhollow -l vba

# Using module options example
python3 staticbypass.py -s ~/shellcode.bin -b mkpivm64 -e IPv4Obfuscate -t shellcoderunner -l c -a sigthief,inputfile=bin/ResourceHacker.exe
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


| Category      | Name            | Languages                | Description | Options |
|:-------------:|:---------------:|:------------------------:|:-----------:|:-------:|
| Delivery      | embedded        | All                      | Shellcode stored within the executable |
|               | webdelivery     | All                      | Download string, raw bytes, or list from specified URL |
|               | regkey          | C#, PS                   | Retrieve shellcode from registry key |
|               | embedtext       | VBA                      | Store shellcode string inside Word document |
| Pre-processor | mkpivm64        | All                      | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | All                      | Convert executable to shellcode |
|               | xorencrypt      | All                      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | All                      | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | All                      | XOR encrypt shellcode with ARX key generation |
|               | LCG             | All                      | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | All                      | Self-decrypting RC4 shellcode stub |
|               | SBOX            | All                      | XOR encrypt shellcode with SBOX and LCG Addition key generation |
| Guardrails    | hostname        | C                        | Terminate execution depending on GetComputerNameA |
|               | username        | C                        | Terminate execution depending on GetUserNameA |
| Transformer   | AESEncrypt      | All                      | AES Encryption |
|               | TinyAES         | C                        | AES Encryption without libraries |
|               | XOREncrypt      | All                      | XOR Encryption |
|               | RC4Encrypt      | All                      | RC4 Encryption |
|               | RSAEncrypt      | C#                       | RSA Encryption |
|               | Rotate          | C                        | Rotate each byte by n bits |
|               | Shuffle         | C                        | Shuffle bytes reversibly |
|               | zlibcompress    | C, C#, Go, Rust, Pascal, PS, Nim | Compression with zlib |
| Obfuscator    | Base64Encode    | All                      | Base64 Encode |
|               | DictObfuscate   | All                      | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | All                      | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | All                      | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | All                      | Convert bytes into MAC addresses |
|               | UUIDEncode      | All                      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | C, C#, PS, Rust, Nim, Go, Pas | Convert bytes into emoji |
|               | Brainfuck       | C                        | Convert bytes into a brainfuck string (slow) |
|               | Whitespace      | C                        | Convert bytes into tabs and spaces |
| Template      | shellcoderunner | All                      | Simple shellcode runner using CreateThread |
|               | processstomp    | C, C#, PS, Rust, Go, VBA | Process hollowing via overwriting entrypoint |
|               | spawnandinject  | All                      | Spawn process and inject into remote thread |
|               | service         | C                        | Template for running executable as service |
|               | processinject   | C                        | Search for explorer.exe and create a remote thread |
|               | delayedhollow   | C                        | Process hollowing with delay |
|               | hellsgate       | C                        | Dynamic API resolution using HellsGate technique |
|               | threadhijack    | C                        | Hijack running thread in existing process |
|               | bzip2           | C                        | Process hollowing using legitimate bzip2 code as cover |
|               | sqlite3         | C                        | Process hollowing using legitimate sqlite3 code as cover |
| Postprocessor | strip           | C, C#, Rust, Pascal, Nim | Strip symbols from executable |
|               | sign            | C, Rust, Go, Pascal, Nim | Sign executable with self-signed certificate |
|               | sigthief        | C, Rust, Go, Pascal, Nim | Steal certificate chain from another file |
|               | resourcecopy    | C, Rust, Go, Pascal, Nim | Copy resources from another executable |
|               | obfell          | PS                       | PowerShell obfuscator by @Jael-G |
|               | junkpile        | PS                       | PowerShell obfuscator by @bobby-tablez |
