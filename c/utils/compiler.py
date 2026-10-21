import subprocess
from pathlib import Path
import sys
import platform

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if platform.system() == 'Linux':
        compiler = 'x86_64-w64-mingw32-gcc'
    elif platform.system() == 'Windows':
        compiler = 'gcc'

    if compiler == 'clang':
        compilerOptions.append('-std=c23')

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
    result = subprocess.run([compiler, sourcefile, '-o', outfile, f'-I{Path(sys.modules['__main__'].__file__).resolve().parent}/c/includes/'] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    else:
        print(result.stderr)
    return outfile