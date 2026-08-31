import subprocess
import os

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if output[-4:] == '.exe':
        sourcefile = f'{output[:-4]}.nim'
        outfile = output
    else:
        sourcefile = f'{output}.nim'
        outfile = f'{output}.exe'
    # Write template to temporary file for compilation
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    env_copy = os.environ.copy()
    result = subprocess.run(['nim', 'c', '-d:mingw'] + compilerOptions + ['-d:release', sourcefile], env=env_copy, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile