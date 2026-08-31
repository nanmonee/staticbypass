import os
from keystone import *

class rotate:

    def __init__(self, arguments: dict) -> None:
        pass

    def apply(self, shellcode: bytes) -> bytes:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.syntax = KS_OPT_SYNTAX_NASM

        encoded = b''
        for i in range(len(shellcode)):
            encoded += (((shellcode[i] << 4) | (shellcode[i] >> 4)) & 255).to_bytes(1)

        decoder_asm = f"""
    lea     rdi, [rel encrypted]    ; rdi -> embedded ciphertext (decrypted in place)
    mov     rdx, {hex(len(shellcode))}                  ; rdx = ciphertext length (immediate)
    xor     rcx, rcx                 ; rcx = index = 0
ror_loop:
    cmp     rcx, rdx                 ; index >= length?
    jae     ror_done                 ; yes -> done
    mov     r8, rcx
    and     r8, 0x0F                 ; key position = index & 15
    mov     al, byte [rdi + rcx]     ; al = target byte
    ror     al, 4                    ; rotate byte by 4 bits
    mov     byte [rdi + rcx], al
    inc     rcx
    jmp     ror_loop
ror_done:
encrypted:
    db {','.join(f'0x{b:02X}' for b in encoded)}
"""
        encoding, count = ks.asm(decoder_asm)
        return bytes(encoding)
