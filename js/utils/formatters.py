def bytes_to_js(bytestring: bytes, name: str) -> str:
    return f'let {name} = new Uint8Array([{ ','.join([hex(x) for x in bytestring]) }]);'

def str_to_js(string: str, name: str,) -> str:
    return f'let {name} = "{string}";'

def list_to_js(itemList: list[str], name: str) -> str:
    return f'let {name} = [ {','.join([f'"{x}"' for x in itemList])}  ];'

def dict_to_js(dictionary: dict[str, int], name: str) -> str:
    return f'let {name} = {{ {','.join([f'"{key}": {value}' for key, value in dictionary.items()])} }};'