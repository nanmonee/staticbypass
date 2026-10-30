import os
import subprocess
import shutil
import json

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfilename = output.rsplit('.', 2)[0]
    outfile = f'{outfilename}.exe'
    srcfile = f'{outfilename}.java'
    env_copy = os.environ.copy()
    open('MessageBoxDemo.java', 'w').write(code)
    data = json.loads(open('reachability-metadata.json', 'r').read())
    data['foreign'] = json.loads('{"downcalls": [' + ','.join(compilerOptions) + '] }')
    open('reachability-metadata.json', 'w').write(json.dumps(data))
    result = subprocess.run(['javac', '-d', 'build', '-J-Xmx2g', 'MessageBoxDemo.java', '--release', '25'], env=env_copy, check=True)
    result = subprocess.run(['native-image.cmd', '--enable-native-access=ALL-UNNAMED', '-H:ConfigurationFileDirectories=.', '-cp', 'build', '-o', outfile, 'MessageBoxDemo'], env=env_copy, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile