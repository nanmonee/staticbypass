import subprocess

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if output[-4:] == '.exe':
        sourcefile = f'{output[:-4]}.pas'
        outfile = output
    else:
        sourcefile = f'{output}.pas'
        outfile = f'{output}.exe'
    # Write template to temporary file for compilation
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['fpc', '-Twin64', sourcefile ]  + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile