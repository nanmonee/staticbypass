import subprocess
import shutil
import os
from pathlib import Path

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    sourcefolder = output.rsplit('.', 2)[0]
    sourcefile = f'{sourcefolder}/Program.cs'
    outfilename = f'{sourcefolder.split('/')[-1]}.exe'
    outfile = f'{sourcefolder}.exe'
    shutil.rmtree(sourcefolder, ignore_errors=True)
    custom_env = os.environ.copy()
    custom_env['TERM'] = 'dumb'
    result = subprocess.run(['dotnet', 'new', 'console', '-o', sourcefolder],env=custom_env, check=True)
    open(sourcefile,'w').write(code)
    print(f'Writing source code to {sourcefile}')
    result = subprocess.run(['dotnet', 'publish', '-c', 'Release', '-r','win-x64', '--self-contained', 'true', '-p:PublishSingleFile=true'], env=custom_env, cwd=sourcefolder, check=True)
    shutil.copy(f'{sourcefolder}/bin/Release/net6.0/win-x64/publish/{outfilename}', outfile)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile