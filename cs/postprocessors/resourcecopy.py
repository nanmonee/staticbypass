import subprocess
import tempfile
from pe_tools import parse_pe, KnownResourceTypes
import time

class resourcecopy:

    def __init__(self, arguments: dict):
        if 'inputfile' in arguments:
            self.inputfile = arguments['inputfile']
        else:
            print('Inputfile required')
            exit(0)

    def apply(self, outfile: str) -> None:
        resourcetf, resourcefilename = tempfile.mkstemp(suffix='.res')
        result = subprocess.run(['wine', 'bin/ResourceHacker.exe','-open', self.inputfile, '-action', 'extract', '-save', resourcefilename, '-mask', ',,'],capture_output=True,  check=True)
        result = subprocess.run(['wine', 'bin/ResourceHacker.exe', '-open', outfile, '-action', 'addoverwrite', '-resource', resourcefilename, '-save', outfile, '-mask', ',,'],capture_output=True, check=True)