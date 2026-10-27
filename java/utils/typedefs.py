typedefs = {
    "VirtualAlloc":"C_POINTER, C_POINTER, C_LONG_LONG, C_INT, C_INT",
    "CreateThread":"C_LONG_LONG, C_POINTER, C_LONG_LONG, C_POINTER, C_POINTER, C_INT, C_POINTER",
    'WaitForSingleObject':'C_INT, C_LONG_LONG, C_INT',
    'VirtualAllocEx':'C_POINTER, C_LONG_LONG, C_POINTER, C_LONG_LONG, C_INT, C_INT',
    'WriteProcessMemory':'C_BOOL, C_LONG_LONG, C_POINTER, C_POINTER, C_LONG_LONG, C_POINTER',
    'CreateRemoteThread':'C_LONG_LONG, C_LONG_LONG, C_POINTER, C_LONG_LONG, C_POINTER, C_POINTER, C_INT, C_POINTER',
    'WaitForSingleObject':'C_INT, C_LONG_LONG, C_INT',
    'CreateProcessA':'C_BOOL, C_POINTER, C_POINTER, C_POINTER, C_POINTER, C_BOOL, C_INT, C_POINTER, C_POINTER, C_POINTER, C_POINTER',

}

ffis = {
    'VirtualAlloc':'{"returnType": "void*","parameterTypes": ["void*","size_t","int","int"]}',
    'CreateThread':'{"returnType": "long long", "parameterTypes": ["void*", "size_t", "void*", "void*", "int", "void*"]}',
    'WaitForSingleObject':'{"returnType": "int", "parameterTypes": ["long long", "int" ]}',
    'VirtualAllocEx':'{"returnType": "void*","parameterTypes": ["long long", "void*","size_t","int","int"]}',
    'CreateProcessA':'{"returnType": "bool", "parameterTypes": ["void*", "void*", "void*", "void*", "bool", "int", "void*", "void*", "void*", "void*" ]}',
    'WriteProcessMemory':'{"returnType": "bool", "parameterTypes": ["long long", "void*", "void*", "long long", "void*" ]}',
    'CreateRemoteThread':'{"returnType": "long long", "parameterTypes": ["long long", "void*", "size_t", "void*", "void*", "int", "void*"]}'
}