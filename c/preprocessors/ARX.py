from keystone import *
import random

class ARX:

    def __init__(self, arguments: dict) -> None:
        pass

    def apply(self, shellcode: bytes) -> bytes:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.syntax = KS_OPT_SYNTAX_INTEL
        initialstate = random.getrandbits(64)
        k = random.getrandbits(64) | 1
        encoded = bytearray()
        state = initialstate
        for i in range(0, len(shellcode)):
            state = (state + k) & 0xFFFFFFFFFFFFFFFF
            state = ((state << 13) | (state >> (64 - 13))) & 0xFFFFFFFFFFFFFFFF
            encoded.append((state & 0xff) ^ shellcode[i])

        decoder_asm = f"""
    lea rdi, [rip + encrypted]
    mov rdx, {hex(len(encoded))}
    movabs r8, {hex(initialstate)}
    movabs r9, {hex(k)}
    xor rcx, rcx
arx_loop:
    cmp rcx, rdx
    jae arx_done
    mov rax, r8
    add rax, r9
    rol rax, {hex(13)}
    xor byte ptr [rdi + rcx], al
    mov r8, rax
    inc rcx
    jmp arx_loop
arx_done:
encrypted:
    .byte {','.join(f'0x{b:02X}' for b in encoded)}
"""

        encoding, count = ks.asm(decoder_asm)
        return bytes(encoding)
