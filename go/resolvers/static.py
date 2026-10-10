import string

class static:
    def __init__(self, arguments):
        self.apicalls = {}

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def template(self, templateCode, transformers, shellcodeSize):
        for _, field_name, _, _ in string.Formatter().parse(templateCode):
            if field_name is not None and field_name not in ['shellcodeSize', 'transformers']:
                self.apicalls[field_name] = ''
        self.resolve()
        return templateCode.format(transformers=transformers, shellcodeSize=shellcodeSize, **self.apicalls)

    def resolve(self):
        for apicall in self.apicalls:
            if apicall[0:2] in ['Rt', 'Nt', 'Zw']:
                self.apicalls[apicall] = f'windows.NewLazySystemDLL("ntdll.dll").NewProc("{apicall}").Call'
            else:
                self.apicalls[apicall] = f'windows.NewLazySystemDLL("kernel32.dll").NewProc("{apicall}").Call'