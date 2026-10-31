import tempfile
import subprocess
import os
import platform
from common.utils.argumentparser import ArgumentParser

class mkpivm64:

    def __init__(self, arguments: dict) -> None:
        parser = ArgumentParser(modulename=self.__class__.__name__)
        parser.add_argument(name='mode', default='rwx', help='mkpivm64 mode. Default requires RWX memory', choices={'rwx':'', 'pack': '--pack', 'rx': '--rx'})
        self.args = parser.parse_args(arguments)
        if platform.system() == 'Linux':
            self.executable = './common/bin/mkpivm64'
        elif platform.system() == 'Windows':
            self.executable = './common/bin/mkpivm64.exe'

    def apply(self, shellcode: bytes) -> bytes:
        fd, filename = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as f:
            f.write(shellcode)
        outtf, outfilename = tempfile.mkstemp()
        result = subprocess.run([self.executable, self.args['mode'], f'{filename}', '-o', f'{outfilename}'])
        if result.returncode == 0:
            output = os.fdopen(outtf, 'rb').read()
        os.remove(filename)
        os.remove(outfilename)
        return output
