from string import Template

def VirtualProtect(lpAddress, dwSize, flNewProtect):
    return Template("""
    DWORD oldProtect;
    {VirtualProtect}($lpAddress, $dwSize, $flNewProtect, &oldProtect);
""").substitute(lpAddress=lpAddress, dwSize=dwSize, flNewProtect=flNewProtect)
    
def NtProtectVirtualMemory(ProcessHandle, BaseAddress, RegionSize, NewProtection):
    return Template("""
    SIZE_T size = $RegionSize;
    ULONG OldProtect; 
    {NtProtectVirtualMemory}($ProcessHandle, &$BaseAddress, &size, $NewProtection, &OldProtect);
""").substitute(ProcessHandle=ProcessHandle, BaseAddress=BaseAddress, RegionSize=RegionSize, NewProtection=NewProtection )

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
    SIZE_T allocationSize = $RegionSize;
    {NtAllocateVirtualMemory}($ProcessHandle, &$output, 0, &allocationSize, $AllocationType, $PageProtection);
""").substitute(output=output, ProcessHandle=ProcessHandle, RegionSize=RegionSize, AllocationType=AllocationType, PageProtection=PageProtection)

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
    SIZE_T bytesWritten = 0;
    {NtWriteVirtualMemory}($ProcessHandle, $destination, $source, $length, &bytesWritten);
""").substitute(destination=destination,ProcessHandle=ProcessHandle,source=source,length=length)

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
