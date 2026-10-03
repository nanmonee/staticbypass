import subprocess
import shutil
import os
from pathlib import Path

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    p = Path(output)
    sourcefolder = f'{p.parent}/{p.stem}'
    shutil.rmtree(sourcefolder, ignore_errors=True)
    custom_env = os.environ.copy()
    custom_env['TERM'] = 'dumb'
    cmdopts = []
    if p.suffix == '.dll':
        result = subprocess.run(['dotnet', 'new', 'classlib', '-o', p.stem],env=custom_env, cwd=p.parent, check=True)
        outfile = f'{p.parent}/{p.stem}.dll'
    elif p.suffix == '.csproj':
        open(output,'w').write(code)
        print(f'Writing source code to {output}')
        return output
    else:
        result = subprocess.run(['dotnet', 'new', 'console', '-o', p.stem],env=custom_env, cwd=p.parent, check=True)
        cmdopts += ['-p:PublishSingleFile=true']
        outfile = f'{p.parent}/{p.stem}.exe'
    open(f'{sourcefolder}/Program.cs','w').write(code)
    print(f'Writing source code to Program.cs')
    for package in compilerOptions:
        subprocess.run(['dotnet', 'add', 'package', package], env=custom_env, cwd=sourcefolder, check=True)
    result = subprocess.run(['dotnet', 'publish', '-c', 'Release', '-r','win-x64', '--self-contained', 'true'] + cmdopts, env=custom_env, cwd=sourcefolder, check=True)
    if p.suffix == '.dll':
        shutil.copy(f'{sourcefolder}/bin/Release/net6.0/win-x64/publish/{p.stem}.dll', outfile)
    else:
        shutil.copy(f'{sourcefolder}/bin/Release/net6.0/win-x64/publish/{p.stem}.exe', outfile)

    if result.returncode == 0:
        print(f'Managed dll saved to {outfile}')
    return outfile