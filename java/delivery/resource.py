import random
import string
from java.utils.formatters import *
import os

class resource:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        os.makedirs("build", exist_ok=True)
        if shellcodeType == "bytes":
            self.type = f"byte[]"
            mode = 'wb'
        elif shellcodeType == "str":
            self.type = f"String"
            mode = 'w'
        elif shellcodeType == "list":
            self.type = f"String[]"
            mode = 'w'
        with open('build/data.bin', mode, newline='\n') as f:
            f.write('\n'.join(shellcode))
            print(f'Shellcode written to data.bin')
        open('reachability-metadata.json', 'w').write('{"resources": [{ "glob": "data.bin" }]}')


    def imports(self) -> list[str]:
        return ['import java.io.InputStream;',
                'import java.io.IOException;',
                'import java.io.UncheckedIOException;']

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        if self.type == "byte[]":
            return f"""
    public static {self.type} {self.name}(){{
        try (InputStream in = MessageBoxDemo.class.getResourceAsStream("/data.bin")) {{
        if (in == null) throw new IllegalStateException("data.bin not found on classpath");
            return in.readAllBytes();
        }} catch (IOException e) {{
            throw new UncheckedIOException(e);
        }}
    }}
"""

        elif self.type == 'String':
            return f"""
    public static {self.type} {self.name}(){{
        try (InputStream in = MessageBoxDemo.class.getResourceAsStream("/data.bin")) {{
        if (in == null) throw new IllegalStateException("data.bin not found on classpath");
            return new String(in.readAllBytes());
        }} catch (IOException e) {{
            throw new UncheckedIOException(e);
        }}
    }}
"""

        elif self.type == 'String[]':
            return f"""
    public static {self.type} {self.name}(){{
        try (InputStream in = MessageBoxDemo.class.getResourceAsStream("/data.bin")) {{
        if (in == null) throw new IllegalStateException("data.bin not found on classpath");
            return (new String(in.readAllBytes())).split("\\n");
        }} catch (IOException e) {{
            throw new UncheckedIOException(e);
        }}
    }}
"""