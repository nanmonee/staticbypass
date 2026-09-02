from keystone import *
import random

class LCG:

    def __init__(self, arguments: dict) -> None:
        pass

    def apply(self, shellcode: bytes) -> bytes:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.syntax = KS_OPT_SYNTAX_INTEL
        initialstate = random.getrandbits(64)
        m = random.getrandbits(64)
        c = random.getrandbits(64)
        encoded = bytearray()
        state = initialstate
        for i in range(0, len(shellcode)):
            state = (state * m) - c
            state = state & 0xFFFFFFFFFFFFFFFF 
            encoded.append((state & 0xff) ^ shellcode[i])

        decoder_asm = f"""
    lea rdi, [rip + encrypted]
    mov rdx, {hex(len(encoded))}
    movabs r8, {hex(initialstate)}
    movabs r9, {hex(m)}
    movabs r10, {hex(c)}
    xor rcx, rcx
arx_loop:
    cmp rcx, rdx
    jae arx_done
    mov rax, r8
    imul rax, r9
    sub rax, r10 
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
