from keystone import *
import random

class SBOX:

    def __init__(self, arguments: dict) -> None:
        pass

    def apply(self, shellcode: bytes) -> bytes:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.syntax = KS_OPT_SYNTAX_INTEL
        sbox = random.sample(range(0, 256), 256)
        sbox_inv = [0]*256
        print(sbox)
        for i in range(0, len(sbox)):
            sbox_inv[sbox[i]] = i
        print(sbox_inv)
        initialstate = random.getrandbits(64)
        m = random.getrandbits(64)
        c = random.getrandbits(64)
        encoded = bytearray()
        state = initialstate
        for i in range(0, len(shellcode)):
            state = (state * m) + c
            state = state & 0xFFFFFFFFFFFFFFFF 
            encoded.append(sbox[shellcode[i]] ^ (state & 0xff))

        decoder_asm = f"""
    lea rdi, [rip + encrypted]
    lea rsi, [rip + sbox]
    movabs r8, {hex(initialstate)}
    movabs r9, {hex(m)}
    movabs r10, {hex(c)}
    mov r11, {hex(len(encoded))}
    xor rcx, rcx
arx_loop:
    cmp rcx, r11
    jae arx_done
    mov rax, r8
    imul rax, r9
    add rax, r10 
    xor byte ptr [rdi + rcx], al
    mov r8, rax
    movzx eax, byte ptr [rdi + rcx]
    mov al, byte ptr [rsi + rax]
    mov byte ptr [rdi + rcx], al
    inc rcx
    jmp arx_loop
arx_done:
encrypted:
    .byte {','.join(f'0x{b:02X}' for b in encoded)}
sbox:
    .byte {','.join(f'0x{b:02X}' for b in sbox_inv)}
"""
        print(decoder_asm)
        encoding, count = ks.asm(decoder_asm)
        return bytes(encoding)
