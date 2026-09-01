import subprocess
import os
import os.path

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outputfile = output.rsplit('.', 2)[0]
    sourcefile = f'{outputfile}.go'
    outfile = f'{outputfile}.exe'
    # Write template to temporary file for compilation
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    env_copy = os.environ.copy()
    env_copy['GOOS'] = 'windows'
    env_copy['GOARCH'] = 'amd64'
    if not os.path.exists('go.mod'):
        subprocess.run(['go', 'mod', 'init', outputfile], env=env_copy, check=True)
    for compilerOption in compilerOptions:
        subprocess.run(['go', 'get', compilerOption], env=env_copy, check=True)
    result = subprocess.run(['go', 'build', '-o', outfile, sourcefile ], env=env_copy, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile