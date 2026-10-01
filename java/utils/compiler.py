import os
import subprocess
import shutil

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfilename = output.rsplit('.', 2)[0]
    outfile = f'{outfilename}.exe'
    srcfile = f'{outfilename}.java'
    env_copy = os.environ.copy()
    open('MessageBoxDemo.java', 'w').write(code)
    open('reachability-metadata.json', 'w').write('{"foreign": {"downcalls": [' + ','.join(compilerOptions) + ']}}')
    result = subprocess.run(['javac', '-d', 'build', 'MessageBoxDemo.java', '--release', '25'], env=env_copy, check=True)
    result = subprocess.run(['native-image.cmd', '--enable-native-access=ALL-UNNAMED', '-H:ConfigurationFileDirectories=.', '-cp', 'build', '-o', outfile, 'MessageBoxDemo'], env=env_copy, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile