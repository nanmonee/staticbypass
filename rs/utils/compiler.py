import os
import subprocess
import shutil

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfilename = output.rsplit('.', 2)[0]
    packagename = outfilename.split('/')[-1]
    outfolder = outfilename
    lib = 'crate-type = ["bin"]'
    if '.dll' in output:
        outfile = f'{outfilename}.dll'
        lib = 'crate-type = ["cdylib"]'
        srcfile = f'{outfolder}/src/lib.rs'
    else:
        outfile = f'{outfilename}.dll'
        srcfile = f'{outfolder}/src/main.rs'
    os.makedirs(f'{outfolder}/src/', exist_ok=True)
    open(srcfile, 'w').write(code)
    open(f'{outfolder}/Cargo.toml', 'w').write(f"""
[package]
name = "{packagename}"
version = "0.1.0"
edition = "2021"

[dependencies]
{'\n'.join(compilerOptions)}

[lib]
{lib}

[profile.release]
""")
    result = subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-pc-windows-gnu'], cwd=outfolder, check=True)
    shutil.copy(f'{outfolder}/target/x86_64-pc-windows-gnu/release/{outfile}', outfile)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile