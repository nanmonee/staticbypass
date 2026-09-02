import subprocess
import shutil
import os
from pathlib import Path

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    p = Path(output)
    sourcefolder = f'{p.parent}/{p.stem}'
    shutil.rmtree(sourcefolder, ignore_errors=True)
    outfile = f'{p.parent}/{p.stem}.exe'
    custom_env = os.environ.copy()
    custom_env['TERM'] = 'dumb'
    result = subprocess.run(['dotnet', 'new', 'console', '-o', p.stem],env=custom_env, cwd=p.parent, check=True)
    open(f'{sourcefolder}/Program.cs','w').write(code)
    print(f'Writing source code to Program.cs')
    result = subprocess.run(['dotnet', 'publish', '-c', 'Release', '-r','win-x64', '--self-contained', 'true', '-p:PublishSingleFile=true'], env=custom_env, cwd=sourcefolder, check=True)
    shutil.copy(f'{sourcefolder}/bin/Release/net6.0/win-x64/publish/{p.stem}.exe', outfile)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile