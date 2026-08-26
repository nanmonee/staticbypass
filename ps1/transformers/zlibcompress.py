import os
import string
import random
import zlib

class zlibcompress:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.uncompressedLength = len(plaintext)
        compressed = zlib.compress(plaintext)
        self.compressedLength = len(compressed)
        return compressed

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [byte[]]$compressedBytes
    )
    begin {{
        $buffer = [System.Collections.Generic.List[byte]]::new()
    }}
    process {{
        $buffer.AddRange($compressedBytes)
    }}
    end {{
        $inputbuffer = $buffer.ToArray()
        $compressed = [System.IO.MemoryStream]::new($inputbuffer, 2, ($inputbuffer.Length - 2))
        $inputstream = [System.IO.Compression.DeflateStream]::new($compressed, [System.IO.Compression.CompressionMode]::Decompress)
        $outputstream = [System.IO.MemoryStream]::new()
        $inputstream.CopyTo($outputstream)
        return $outputstream.ToArray()
    }}
}}
"""
