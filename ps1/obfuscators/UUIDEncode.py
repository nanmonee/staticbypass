import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes_le = chunk)))
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
        foreach ($UUID in $buffer){{
            $guid = [guid]$UUID
            $decoded.AddRange($guid.ToByteArray())
        }}
        return $decoded
    }}
}}
"""