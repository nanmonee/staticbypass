import os
import string
import random
import zlib

class zlibcompress:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return ['use std::io::Read;','use flate2::read::ZlibDecoder;']

    def compilerOptions(self) -> list[str]:
        return ['flate2 = "1.1.9"']

    def encode(self, plaintext: bytes) -> bytes:
        self.uncompressedLength = len(plaintext)
        compressed = zlib.compress(plaintext)
        self.compressedLength = len(compressed)
        return compressed

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(compressed: &[u8]) -> Vec<u8>{{
    let mut zlibstream = ZlibDecoder::new(&compressed[..]);
    let mut decompressed = Vec::new();
    zlibstream.read_to_end(&mut decompressed).unwrap();
    decompressed
}}
"""
