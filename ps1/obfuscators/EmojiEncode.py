import random
import string

class EmojiEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        encoded = ""
        for i in range(0, len(decoded)):
            encoded += chr(0x1f400 + decoded[i])
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$Encoded
    )
    process {{
        $emojibytes = [System.Text.Encoding]::UTF8.GetBytes($Encoded)
        [byte[]]$bytes = [System.Array]::CreateInstance([byte],$Encoded.Length/2)
        for (($i = 0); $i -lt $Encoded.Length/2; $i++)
        {{
            $1 = ($emojibytes[$i*4] -band 0x07) -shl 18
            $2 = ($emojibytes[$i*4 + 1] -band 0x3F) -shl 12
            $3 = ($emojibytes[$i*4 + 2] -band 0x3F) -shl 6
            $4 = ($emojibytes[$i*4 + 3] -band 0x3F)
            $bytes[$i] = ($1 -bor $2 -bor $3 -bor $4) -band 255
        }}
        return $bytes
    }}
}}
"""
