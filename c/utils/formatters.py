def bytes_to_c(bytestring: bytes, name: str) -> str:
    return f'static const unsigned char {name}[] = ' + '{' + ','.join([f'{hex(val)}' for val in bytestring]) + '};'

def str_to_c(string: str, name: str) -> str:
    return f'static const unsigned char {name}[] = "{string}\\0";'

def list_to_c(itemList: list[str], name: str) -> str:
    encodedString = ",".join([f'"{x}"' for x in itemList])
    return f'static const unsigned char *{name}[] = {{{encodedString}}};'

def dict_to_c(dictionary: dict[str, int], name: str) -> str:
    codeblock = ''
    for key, value in dictionary.items():
        codeblock += f'\tset("{key}", {value});\n'
    return codeblock