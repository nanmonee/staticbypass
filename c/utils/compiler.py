import subprocess
from pathlib import Path

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    p = Path(output)
    source = f'{p.parent}/{p.stem}'
    if '-shared' in compilerOptions:
        sourcefile = f'{source}.c'
        outfile = f'{source}.dll'
    else:
        sourcefile = f'{source}.c'
        outfile = f'{source}.exe'
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['x86_64-w64-mingw32-gcc', sourcefile, '-o', outfile, '--static'] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile