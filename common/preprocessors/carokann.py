import os
from keystone import *

class carokann:

    def __init__(self, arguments: dict) -> None:
        self.key = b'\x01\x02\x03\x04'
        if 'key' in arguments:
            self.key = arguments['args'].encode()

    def apply(self, shellcode: bytes) -> bytes:
        encrypted = bytes(shellcode[i] ^ self.key[i % len(self.key)] for i in range(0, len(shellcode)))
        return encrypted
