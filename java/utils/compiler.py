import os
import subprocess
import shutil
import json
import tempfile

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfilename = output.rsplit('.', 2)[0]
    outfile = f'{outfilename}.exe'
    srcfile = f'{outfilename}.java'
    tempdir = tempfile.gettempdir()
    env_copy = os.environ.copy()
    open('Output.java', 'w').write(code)
    data = json.loads(open(f'{tempdir}/reachability-metadata.json', 'r').read())
    data['foreign'] = json.loads('{"downcalls": [' + ','.join(compilerOptions) + '] }')
    open(f'{tempdir}/reachability-metadata.json', 'w').write(json.dumps(data))
    result = subprocess.run(['javac', '-d', tempdir, '-J-Xmx2g', 'Output.java', '--release', '25'], env=env_copy, check=True)
    result = subprocess.run(['native-image.cmd', '--enable-native-access=ALL-UNNAMED', f'-H:ConfigurationFileDirectories={tempdir}', '-cp', tempdir, '-o', outfile, 'Output'], env=env_copy, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile