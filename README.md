# StaticBypass - Template-based, modular, multi-language, shellcode obfuscator and compiler

## Features
- Takes in a raw shellcode or executable file, applies encryptors and obfuscators, formats it, places it into a template, and compiles it
- Supports C, C#, PowerShell, VBA, Rust, Go, Pascal, and Nim
- Supports Typescript using Bun, Javascript using Deno, and Java using GraalVM
- Automates placing VBA code into a word document
- Supports AES, XOR, and RC4 encryption, and Dictionary, UUID, IPv4, IPv6, and MAC address obfuscation
- Designed to bypass static and possible dynamic detection methods

## Usage
```
python3 staticbypass.py -h
usage: staticbypass.py [-h] [-e [TRANSFORMERS ...]] -s SHELLCODE -t TEMPLATE -l {rs,vba,c,pas,nim,cs,ts,js,go,ps1,java} [-f OBFUSCATOR] [-g [GUARDRAILS ...]] [-r RESOLVER] [-b [PREPROCESSORS ...]] [-a [POSTPROCESSORS ...]] [-d DELIVERY] [-w WRAPPER] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -e [TRANSFORMERS ...], --transformers [TRANSFORMERS ...]
                        Transformers encrypt or encode the shellcode and is decrypted or decoded at runtime.
  -s SHELLCODE, --shellcode SHELLCODE
                        Specifies the raw binary shellcode file
  -t TEMPLATE, --template TEMPLATE
                        Template that the shellcode and deobfuscation code will be placed into.
  -l {rs,vba,c,pas,nim,cs,ts,js,go,ps1,java}, --language {rs,vba,c,pas,nim,cs,ts,js,go,ps1,java}
                        Language used to write and compile
  -f OBFUSCATOR, --obfuscator OBFUSCATOR
                        Obfuscators transform the transformed shellcode bytes into other formats, such as strings.
  -g [GUARDRAILS ...], --guardrails [GUARDRAILS ...]
                        Guardrails stop execution if some condition is met.
  -r RESOLVER, --resolver RESOLVER
                        Controls how Windows API calls are resolved.
  -b [PREPROCESSORS ...], --preprocessors [PREPROCESSORS ...]
                        Preprocessors modify the shellcode but are self decoding.
  -a [POSTPROCESSORS ...], --postprocessors [POSTPROCESSORS ...]
                        Postprocessors obfuscate the resulting exe or script, e.g. packers
  -d DELIVERY, --delivery DELIVERY
                        Delivery defines where the obfuscated shellcode is retrieved
  -w WRAPPER, --wrapper WRAPPER
                        Wrap execution template in other code for obfuscation
  -o OUTPUT, --output OUTPUT
                        Output file name
```

## Examples
```
# Generic Defender Bypass
python3 staticbypass.py --obfuscator DictObfuscate --transformers XOREncrypt RC4Encrypt AESEncrypt --shellcode ~/shellcode.bin --template shellcoderunner --language cs

# Indirect Syscalls using TartarusGate to resolve windows API call
python3 staticbypass.py --obfuscator DictObfuscate --transformers XOREncrypt RC4Encrypt AESEncrypt --shellcode ~/shellcode.bin --template spawnandinject,spawn=NtCreateUserProcess,allocation=NtAllocateVirtualMemory,write=NtWriteVirtualMemory,protect=NtProtectVirtualMemory,execution=NtQueueApcThread,close=NtClose --language c --resolver tartarusgatehash

# Spawn a process and inject into it using VM-based obfuscation
python3 staticbypass.py -s ~/shellcode.bin -b mkpivm64 -e IPv4Obfuscate -t spawnandinject,perm=rwx -l c -a strip

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
- Add arguments to compiler
- Finish install script
- Increase windows support

## Installation
### Install pre-reqs
```
./install.sh
```
Will get you most of the way there, still have yet to test it properly

### Download project
```
git clone https://github.com/nanmonee/staticbypass.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Currently Implemented

<details>
  <summary>C</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Guardrails    | hostname        | Terminate execution depending on GetComputerNameA |
|               | username        | Terminate execution depending on GetUserNameA |
| Transformer   | AESEncrypt      | AES Encryption |
|               | TinyAES         | AES Encryption without libraries |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | Rotate          | Rotate each byte by n bits |
|               | Shuffle         | Shuffle bytes reversibly |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
|               | Brainfuck       | Convert bytes into a brainfuck string (slow) |
|               | Whitespace      | Convert bytes into tabs and spaces |
|               | NetBIOSEncode   | Encode bytes using NETBIOS name encoding  |
| Template      | shellcoderunner | Shellcode execution in-process using various methods |
|               | processstomp    | Process hollowing via overwriting entrypoint |
|               | processinject   | Spawn or inject into process via various methods |
|               | processhollow   | Spawn process, unmap and write new PE |
|               | tp_timer        | TP_TIMER injection |
|               | modulestomp     | Load module and stomp its code |
|               | earlycascade    | Early cascade injection |
|               | carokann        | Process injection using CaroKann (requires carokann pre-processor) |
| Resolvers     | static          | Static function resolution |
|               | dynamic         | Dynamic function resolution using GetProcAddress |
|               | pebwalk         | PEB walk |
|               | pebwalkhash     | PEB walk using hashes instead of strings |
|               | hellsgatehash   | Indirect syscalls using Hells Gate |
|               | halosgatehash   | Indirect syscalls using Halos Gate |
|               | tartarusgatehash| Indirect syscalls using Tartarus Gate |
|               | tartarusgatehashrap | Indirect syscalls using Tartarus Gate with Return Address Patching |
| Wrappers      | main            | Default wrapper |
|               | rundll          | Execute code on DLL load |
|               | service         | Run executable as service |
|               | bzip2           | bzip2 code |
|               | sqlite3         | sqlite3 code |
|               | rect_pack       | rect pack code |
| Postprocessor | strip           | Strip symbols from executable |
|               | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |

</details>

<details>
  <summary>CS</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
|               | regkey          | Retrieve shellcode from registry key |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | NOPmask         | Payload encryption by @whoamiamleo |'
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Guardrails    | hostname        | Terminate execution depending on GetComputerNameA |
|               | username        | Terminate execution depending on GetUserNameA |
| Transformer   | AESEncrypt      | AES Encryption |
|               | RSAEncrypt      | RSA Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | processstomp    | Process hollowing via overwriting entrypoint |
|               | spawnandinject  | Spawn process and inject into remote thread |
|               | asynccallback   | Asynchronous callback execution using EnumUILanguagesA |
| Resolvers     | static          | Static function resolution |
|               | dynamic         | Dynamic function resolution using GetProcAddress |
| Wrappers      | main            | Default wrapper |
|               | rundll          | Execute code on DLL load |
|               | msbuild         | Execute csharp code as part of msbuild .csproj file |
|               | installutil     | Compile to dll that you can execute through InstallUtil |
|               | dotnet2js       | Create managed dll for converting into .js and .hta files using DotNetToJs |
| Postprocessor | strip           | Strip symbols from executable |
|               | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |
|               | dotnettojscript | Convert managed dll to .js, .hta, or .xsl files for execution using wscript.exe, and mshta.exe |

</details>

<details>
  <summary>Go</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | processstomp    | Process hollowing via overwriting entrypoint |
|               | spawnandinject  | Spawn process and inject into remote thread |
|               | carokann        | Process injection using CaroKann (requires carokann preprocessor) |
| Resolvers     | static          | Static function resolution |
|               | dynamic         | Dynamic function resolution using GetProcAddress |
| Wrappers      | main            | Default wrapper |
|               | rundll          | Execute code on DLL load |
| Postprocessor | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |

</details>

<details>
  <summary>Rust</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Guardrails    | hostname        | Terminate execution depending on GetComputerNameA |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | processstomp    | Process hollowing via overwriting entrypoint |
|               | spawnandinject  | Spawn process and inject into remote thread |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |
|               | rundll          | Execute code on DLL load |
|               | zoxide          | zoxide |
| Postprocessor | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |
|               | strip           | Strip symbols from executable |

</details>

<details>
  <summary>Nim</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
| Resolvers     | static          | Static function resolution |
|               | dynamic         | Dynamic function resolution using GetProcAddress |
| Wrappers      | main            | Default wrapper |
|               | rundll          | Execute code on DLL load |
| Postprocessor | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |
|               | strip           | Strip symbols from executable |

</details>

<details>
  <summary>TypeScript</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
|               | carokann        | Process injection using CaroKann (requires carokann preprocessor) |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |
| Postprocessor | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |
|               | strip           | Strip symbols from executable |

</details>

<details>
  <summary>JavaScript</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |

</details>

<details>
  <summary>Java</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |

</details>

<details>
  <summary>Pascal</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |
| Postprocessor | sign            | Sign executable with self-signed certificate |
|               | sigthief        | Steal certificate chain from another file |
|               | resourcecopy    | Copy resources from another executable |
|               | strip           | Strip symbols from executable |
</details>

<details>
  <summary>PowerShell</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
|               | regkey          | Retrieve shellcode from registry key |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
|               | zlibcompress    | Compression with zlib |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
|               | EmojiEncode     | Convert bytes into emoji |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
|               | processstomp    | Process hollowing via overwriting entrypoint |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |
| Postprocessor | obfell          | PowerShell obfuscator by @Jael-G |
|               | junkpile        | PowerShell obfuscator by @bobby-tablez |

</details>

<details>
  <summary>VBA</summary>

| Category      | Name            | Description | 
|:-------------:|:---------------:|:-----------:|
| Delivery      | embedded        | Shellcode stored within the executable |
|               | webdelivery     | Download string, raw bytes, or list from specified URL |
|               | embedtext       | Store shellcode string inside Word document |
| Pre-processor | mkpivm64        | Virtualize shellcode for obfuscation (requires template with RWX) by @D7EAD |
|               | donut           | Convert executable to shellcode |
|               | xorencrypt      | XOR encrypt shellcode with self-decrypting stub (requires RWX) |
|               | rotate          | Rotate shellcode with self-decoding stub (requires RWX) |
|               | ARX             | XOR encrypt shellcode with ARX key generation |
|               | LCG             | XOR encrypt shellcode with LCG Subtraction key generation |
|               | RC4             | Self-decrypting RC4 shellcode stub |
|               | SBOX            | XOR encrypt shellcode with SBOX and LCG Addition key generation |
|               | NOPmask         | Payload encryption by @whoamiamleo |
|               | carokann        | XOR encryption with key 0x01020304 for use with the carokann template |
| Transformer   | AESEncrypt      | AES Encryption |
|               | XOREncrypt      | XOR Encryption |
|               | RC4Encrypt      | RC4 Encryption |
| Obfuscator    | Base64Encode    | Base64 Encode |
|               | DictObfuscate   | Convert bytes into randomly picked dictionary words |
|               | IPv4Obfuscate   | Convert bytes into IPv4 addresses |
|               | IPv6Obfuscate   | Convert bytes into IPv6 addresses |
|               | MACObfuscate    | Convert bytes into MAC addresses |
|               | UUIDEncode      | Convert bytes into UUIDv4 strings |
| Template      | shellcoderunner | Simple shellcode runner using CreateThread |
|               | spawnandinject  | Spawn process and inject into remote thread |
|               | processstomp    | Process hollowing via overwriting entrypoint |
| Resolvers     | static          | Static function resolution |
| Wrappers      | main            | Default wrapper |

</details>
