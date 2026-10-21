typedefs = {
    "VirtualAlloc":"IntPtr VirtualAlloc(IntPtr lpAddress, ulong dwSize, uint flAllocationType, uint flProtect);",
    "CreateThread":"IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);",
    "WaitForSingleObject":"UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);",
    "CreateProcessA":"bool CreateProcessA(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, [In] ref STARTUPINFO lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);",
    "VirtualAllocEx":"IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, ulong dwSize, uint flAllocationType, uint flProtect);",
    "ResumeThread":"uint ResumeThread(IntPtr hThread);",
    "WriteProcessMemory":"bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, ulong nSize, out IntPtr lpNumberOfBytesWritten);",
    "CreateRemoteThread":"IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out IntPtr lpThreadId);",
    "CloseHandle":"bool CloseHandle(IntPtr hObject);",
    "ReadProcessMemory":"bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, [Out] byte[] lpBuffer, ulong dwSize, out IntPtr lpNumberOfBytesRead);",
    "ZwQueryInformationProcess":"int ZwQueryInformationProcess(IntPtr hProcess, int procInformationClass, ref PROCESS_BASIC_INFORMATION procInformation, uint ProcInfoLen, ref uint retlen);",
    "VirtualProtect":"bool VirtualProtect(IntPtr lpAddress, ulong dwSize, uint flNewProtect, out IntPtr lpflOldProtect);",
    "VirtualProtectEx":"bool VirtualProtectEx(IntPtr hProcess, IntPtr lpAddress, ulong dwSize, uint flNewProtect, out IntPtr lpflOldProtect);"

}