import string

class dynamic:
    def __init__(self, arguments):
        self.apicalls = {}

    def imports(self) -> list[str]:
        return ['syscall']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """

type syscallAddress struct {
    functionAddress uintptr
}

func callWindowsAPI(functionName, library string) syscallAddress {

    libraryHandle, _ := windows.LoadLibrary(library)

    funcAddress, _ := windows.GetProcAddress(libraryHandle, functionName)

    return syscallAddress{functionAddress: funcAddress}
}

func (s syscallAddress) Call(args ...uintptr) (uintptr, uintptr, syscall.Errno) {
    return syscall.SyscallN(s.functionAddress, args...)
}
"""

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            if apicall[0:2] in ['Rt', 'Nt', 'Zw']:
                self.apicalls[apicall] = f'callWindowsAPI("{apicall}", "ntdll.dll").Call'
            else:
                self.apicalls[apicall] = f'callWindowsAPI("{apicall}", "kernel32.dll").Call'