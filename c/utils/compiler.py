import subprocess

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if '-shared' in compilerOptions:
        if 'dll' not in output:
            sourcefile = f'{output}.c'
            outfile = f'{output}.dll'
        else:
            sourcefile = f'{output[:-4]}.c'
            outfile = f'{output}'
    elif output[-4:] == '.exe':
        sourcefile = f'{output[:-4]}.c'
        outfile = output[:-4]
    else:
        sourcefile = f'{output}.c'
        outfile = f'{output}'
    # Write template to temporary file for compilation
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['x86_64-w64-mingw32-gcc' , sourcefile, '-o', outfile, '--static'] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile