typedefs = {
    'VirtualAlloc':'VirtualAlloc: { parameters: ["pointer", "usize", "u32", "u32"], result: "pointer", }',
    'CreateThread':'CreateThread: { parameters: ["pointer", "usize", "pointer", "pointer", "u32", "pointer"], result: "pointer", }',
    'WaitForSingleObject':'WaitForSingleObject: { parameters: ["pointer", "u32"], result: "u32", }',
    'CreateProcessA':'CreateProcessA: { parameters: ["buffer", "buffer", "buffer", "buffer", "i32", "u32", "buffer", "buffer", "buffer", "buffer"], result: "i32", }',
    'WriteProcessMemory':'WriteProcessMemory: { parameters: ["pointer", "pointer", "buffer", "usize", "pointer"], result: "i32", }',
    'VirtualAllocEx':'VirtualAllocEx: { parameters: ["pointer", "pointer", "usize", "u32", "u32"], result: "pointer", }',
    'CreateRemoteThread':'CreateRemoteThread: { parameters: ["pointer", "pointer", "usize", "pointer", "pointer", "u32", "pointer"], result: "pointer", }',
    'CloseHandle':'CloseHandle: { parameters: ["pointer"], result: "i32", }',
}