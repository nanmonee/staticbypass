import subprocess

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    filename = output.rsplit('.', 2)[0]
    sourcefile = f'{filename}.lua'
    outfile = f'{filename}.exe'
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['rtc', '-lc', sourcefile, '-o', outfile] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile