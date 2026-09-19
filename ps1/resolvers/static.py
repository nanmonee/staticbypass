from string import Template

class static:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return ''

    def resolve(self, apicalls):
        resolved = {}
        for apicall in apicalls:
            resolved[apicall] = apicall
        return resolved