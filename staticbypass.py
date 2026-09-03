import argparse
import importlib
import importlib.util
import sys

def load_module(language: str, category: str, item: str) -> type:
    spec = importlib.util.spec_from_file_location(item, f'{language}/{category}/{item}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, item)

def parse_module_args(argument_string: str) -> tuple[str, dict]:
    split = str(argument_string).split(',')
    module = split[0]
    arguments = {}
    if (len(split) != 1):
        for item in split[1:]:
            if '=' in item:
                key, _, value = item.partition('=')
                arguments[key] = value
            else:
                arguments[item] = True
    return module, arguments

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', "--transformers", type=str, nargs='*', required=False, help='Transformers encrypt or encode the shellcode and is decrypted or decoded at runtime.')
    parser.add_argument('-s', "--shellcode", type=str, required=True, help='Specifies the raw binary shellcode file')
    parser.add_argument('-t', "--template", type=str, required=True, help='Template that the shellcode and deobfuscation code will be placed into.')
    parser.add_argument('-l', "--language", type=str, choices={"c","cs","ps1","vba", "rs", "go", "pas", "nim"}, required=True, help='Language used to write and compile')
    parser.add_argument('-f', "--obfuscator", type=str, required=False, help='Obfuscators transform the transformed shellcode bytes into other formats, such as strings.')
    parser.add_argument('-b', "--preprocessors", type=str, nargs = '*', required=False, help='Preprocessors modify the shellcode but are self decoding.')
    parser.add_argument('-a', "--postprocessors", type=str, nargs='*', required=False, help='Postprocessors obfuscate the resulting exe or script, e.g. packers')
    parser.add_argument('-d', "--delivery", type=str, required=False, default="embedded", help='Delivery defines where the obfuscated shellcode is retrieved')
    parser.add_argument('-o', "--output", type=str, required=False, default="output", help='Output file name')
    args = parser.parse_args()

    shellcode = open(args.shellcode, 'rb').read()

    compilerOptions = []
    codeblocks = ''
    if args.language == 'cs':
        transformers = 'byte[] shellcode = {shellcode};'
    elif args.language == 'c':
        transformers = 'unsigned char *shellcode = {shellcode};'
    elif args.language == 'vba':
        transformers = 'shellcode = {shellcode}'
    elif args.language == 'ps1':
        transformers = '[Byte[]]$shellcode = {shellcode}'
    elif args.language == 'rs':
        transformers = 'let shellcode = {shellcode};'
    elif args.language == 'go':
        transformers = 'shellcode := {shellcode};'
    elif args.language == 'pas':
        transformers = 'shellcode := {shellcode};'
    elif args.language == 'nim':
        transformers = 'let shellcode = {shellcode};'
    imports = []

    if args.preprocessors:
        for preprocessor in args.preprocessors:
            preprocessorItem, arguments = parse_module_args(preprocessor)
            preprocessorObject = load_module(args.language, 'preprocessors', preprocessorItem)(arguments)
            shellcode = preprocessorObject.apply(shellcode)

    shellcodeSize = len(shellcode)

    if args.transformers:
        for transformer in args.transformers:
            transformersItem, arguments = parse_module_args(transformer)
            transformersObject = load_module(args.language, 'transformers', transformersItem)(arguments)
            transformedShellcode = transformersObject.encode(shellcode)
            codeblocks += transformersObject.codeblock()
            transformers = transformersObject.transformer(transformers)
            compilerOptions += transformersObject.compilerOptions()
            imports += transformersObject.imports()
            shellcode = transformedShellcode

    # Obfuscate shellcode
    if args.obfuscator:
        obfuscator, arguments = parse_module_args(args.obfuscator)
        obfuscatorObject = load_module(args.language, 'obfuscators', obfuscator)(arguments)
        obfuscatedShellcode = obfuscatorObject.obfuscate(shellcode)
        codeblocks += obfuscatorObject.codeblock()
        transformers = obfuscatorObject.transformer(transformers)
        imports += obfuscatorObject.imports()
        compilerOptions += obfuscatorObject.compilerOptions()
        shellcode = obfuscatedShellcode

    deliveryItem, arguments = parse_module_args(args.delivery)
    deliveryObject = load_module(args.language, 'delivery', deliveryItem)(shellcode, arguments)
    codeblocks += deliveryObject.codeblock()
    transformers = deliveryObject.transformer(transformers)
    imports += deliveryObject.imports()
    compilerOptions += deliveryObject.compilerOptions()

    compilerOptions = list(dict.fromkeys(compilerOptions))

    # Load template options
    template, arguments = parse_module_args(args.template)
    templateObject = load_module(args.language, 'templates', template)(arguments)
    compilerOptions += templateObject.compilerOptions()
    imports = templateObject.imports() + imports
    # Remove duplicates while retaining order
    if args.language == 'pas':
        imports = ','.join(list(dict.fromkeys(imports)))
    else:
        imports = '\n'.join(list(dict.fromkeys(imports)))
    formattedCode = templateObject.template(imports, codeblocks, transformers, shellcodeSize)

    compiler = importlib.import_module(f'{args.language}.utils.compiler')
    outfile = compiler.compile(formattedCode, args.output, compilerOptions)

    if args.postprocessors:
        for postprocessor in args.postprocessors:
            postprocessorItem, arguments = parse_module_args(postprocessor)
            postprocessorObject = load_module(args.language, 'postprocessors', postprocessorItem)(arguments)
            postprocessorFunction = getattr(postprocessorObject, 'apply')
            postprocessorFunction(outfile)

if __name__ == "__main__":
    main()

