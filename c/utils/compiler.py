import subprocess

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    filename = output.rsplit('.', 2)[0]
    if '-shared' in compilerOptions:
        sourcefile = f'{filename}.c'
        outfile = f'{filename}.dll'
    else:
        sourcefile = f'{filename}.c'
        outfile = f'{filename}'
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['x86_64-w64-mingw32-gcc' , sourcefile, '-o', outfile, '--static'] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile