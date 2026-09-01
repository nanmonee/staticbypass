import tempfile
import subprocess
import os

class donut:

    def __init__(self, arguments: dict) -> None:
        self.arguments = []
        if 'args' in arguments:
            self.arguments += ['-p', arguments['args']]

    def apply(self, shellcode: bytes) -> bytes:
        fd, filename = tempfile.mkstemp(suffix='.exe')
        with os.fdopen(fd, 'wb') as f:
            f.write(shellcode)
        outtf, outfilename = tempfile.mkstemp()
        
        result = subprocess.run(['wine', './bin/donut.exe', '-i', filename, '-b', '1', '-k', '2', '-o', outfilename] + self.arguments, check=True)
        
        if result.returncode == 0:
            output = os.fdopen(outtf, 'rb').read()
        os.remove(filename)
        os.remove(outfilename)
        return output
