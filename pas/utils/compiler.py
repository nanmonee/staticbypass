import subprocess

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfilename = output.rsplit('.', 2)[0]
    sourcefile = f'{outfilename}.pas'
    outfile = f'{outfilename}.exe'
    # Write template to temporary file for compilation
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['fpc', '-Twin64', sourcefile ]  + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile