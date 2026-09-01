import codecs

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfilename = output.rsplit('.', 2)[0]
    outfile = f'{outfilename}.ps1'
    print(f'Writing source code to {outfile}')
    codecs.open(outfile, 'w', 'utf-8-sig').write(code)
    return outfile