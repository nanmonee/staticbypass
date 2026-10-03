import subprocess
import shutil
import os
from pathlib import Path
import platform

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    p = Path(output)

    if 'csproj' in compilerOptions:
        open(f'{p.with_suffix("")}.csproj','w').write(code)
        print(f'Writing csproj to {output}')
        return output

    cmdopts = []

    if 'dotnet' in compilerOptions:
        result = subprocess.run(['dotnet', '--version'], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            sdkversion = result.stdout.split('.')[0]
        else:
            print('dotnet not installed or not on PATH')
            exit(0)

        custom_env = os.environ.copy()
        custom_env['TERM'] = 'dumb'
        cmdopts = []
        shutil.rmtree(p.stem)
        sourcefolder = f'{p.stem}'
        if 'dll' in compilerOptions:
            if platform.system() != 'Windows':
                print("Building native .NET DLLs is only supported on Windows")
                exit(0)
            result = subprocess.run(['dotnet', 'new', 'classlib', '-o', p.stem],env=custom_env, cwd=p.parent, check=True)
            cmdopts += ['-p:PublishAot=true', '-p:NativeLib=Shared']
            outfile = f'{p.with_suffix("")}.dll'
            sourcefile = f'{sourcefolder}/Class1.cs'
        else:
            result = subprocess.run(['dotnet', 'new', 'console', '-o', p.stem],env=custom_env, cwd=p.parent, check=True)
            cmdopts += ['-p:PublishSingleFile=true', '--self-contained', 'true']
            outfile = f'{p.with_suffix("")}.exe'
            sourcefile = f'{sourcefolder}/Program.cs'
        open(sourcefile,'w').write(code)
        print(f'Writing source code to {sourcefile}')
        result = subprocess.run(['dotnet', 'publish', '-c', 'Release', '-r','win-x64'] + cmdopts, env=custom_env, cwd=sourcefolder, check=True)
        if 'dll' in compilerOptions:
                shutil.copy(f'{sourcefolder}/bin/Release/net{sdkversion}.0/win-x64/publish/{p.stem}.dll', outfile)
        else:
            shutil.copy(f'{sourcefolder}/bin/Release/net{sdkversion}.0/win-x64/publish/{p.stem}.exe', outfile)
        if result.returncode == 0:
            print(f'Output saved to {outfile}')
        return outfile
    else:
        if 'dll' in compilerOptions:
            cmdopts = [f'/out:{p.with_suffix("")}.dll', '/target:library']
            outfile = f'{p.with_suffix("")}.dll'
        else:
            cmdopts = [f'/out:{p.with_suffix("")}.exe']
            outfile = f'{p.with_suffix("")}.exe'
        print(f'Writing code to {p.parent}/{p.stem}.cs')
        open(f'{p.parent}/{p.stem}.cs','w').write(code)
        if platform.system() == 'Linux':
            result = subprocess.run(['mcs', f'{p.parent}/{p.stem}.cs'] + cmdopts, check=True)
        else:
            result = subprocess.run(['csc.exe', f'{p.parent}/{p.stem}.cs'] + cmdopts, check=True)
        if result.returncode == 0:
            print(f'Output saved to {outfile}')