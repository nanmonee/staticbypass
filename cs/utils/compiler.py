import subprocess
import shutil
import os

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if output[-4:] == '.exe':
        sourcefolder = output[:-4]
        sourcefile = f'{output[:-4]}/Program.cs'
        outfile = output
    else:
        sourcefolder = output
        sourcefile = f'{output}/Program.cs'
        outfile = f'{output}.exe'
    shutil.rmtree(sourcefolder, ignore_errors=True)
    custom_env = os.environ.copy()
    custom_env['TERM'] = 'xterm'
    result = subprocess.run(['dotnet', 'new', 'console', '-o', sourcefolder],env=custom_env, check=True)
    open(sourcefile,'w').write(code)
    print(f'Writing source code to {sourcefile}')
    result = subprocess.run(['dotnet', 'publish', '-c', 'Release', '-r','win-x64', '--self-contained', 'true', '-p:PublishSingleFile=true'], env=custom_env, cwd=sourcefolder, check=True)
    shutil.copy(f'{sourcefolder}/bin/Release/net6.0/win-x64/publish/{outfile}', outfile)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile