import tempfile
import subprocess
import os
import platform

class mkpivm64:

    def __init__(self, arguments: dict) -> None:
        self.arguments = []
        if 'pack' in arguments:
            self.arguments.append('--pack')

    def apply(self, shellcode: bytes) -> bytes:
        fd, filename = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as f:
            f.write(shellcode)
        outtf, outfilename = tempfile.mkstemp()
        if platform.system() == 'Linux':
            result = subprocess.run(['wine', './bin/mkpivm64.exe'] + self.arguments + [f'{filename}', '-o', f'{outfilename}'])
        else:
            result = subprocess.run(['./bin/mkpivm64.exe']  + self.arguments + [f'{filename}', '-o', f'{outfilename}'])
        if result.returncode == 0:
            output = os.fdopen(outtf, 'rb').read()
        os.remove(filename)
        os.remove(outfilename)
        return output
