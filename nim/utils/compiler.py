import subprocess
import os

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outputfile = output.rsplit('.', 2)[0]
    sourcefile = f'{outputfile}.nim'
    outfile = f'{outputfile}.exe'
    # Write template to temporary file for compilation
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    env_copy = os.environ.copy()
    result = subprocess.run(['nim', 'c', '-d:mingw'] + compilerOptions + [f'-o:{outfile}', '-d:release', sourcefile], env=env_copy, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile