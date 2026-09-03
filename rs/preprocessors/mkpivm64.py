import tempfile
import subprocess
import os

class mkpivm64:

    def __init__(self, arguments: dict) -> None:
        self.arguments = []
        if 'mode' in arguments:
            if arguments['mode'] == 'pack':
                self.arguments.append('--pack')

    def apply(self, shellcode: bytes) -> bytes:
        fd, filename = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as f:
            f.write(shellcode)
        outtf, outfilename = tempfile.mkstemp()
        result = subprocess.run(['./bin/mkpivm64'] + self.arguments + [f'{filename}', '-o', f'{outfilename}'])
        if result.returncode == 0:
            output = os.fdopen(outtf, 'rb').read()
        os.remove(filename)
        os.remove(outfilename)
        return output
