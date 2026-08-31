import subprocess
import platform

class strip:

    def __init__(self, arguments: dict) -> None:
        pass

    def apply(self, outfile: str) -> None:
        if platform.system() == 'Linux':
            result = subprocess.run(['strip', '--strip-all', f'{outfile}'])