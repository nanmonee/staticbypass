def bytes_to_java(bytestring: bytes, name: str) -> str:
    # return f'let {name}= vec![{','.join([f'{hex(val)}' for val in bytestring])}];'
    return f'byte[] {name} = {{ {','.join([f'(byte) {hex(val)}' for val in bytestring])} }};'

def str_to_java(string: str, name: str) -> str:
    return f'String {name} = "{string}";'

def list_to_java(itemList: list[str], name: str) -> str:
    return f'String[] {name} = {{ {','.join([f'"{x}"' for x in itemList])} }};'

def dict_to_java(dictionary: dict[str, int], name: str) -> str:
    return f'Map<String, Integer> {name} = Map.ofEntries( {','.join([f'entry("{key}", {value})' for key,value in dictionary.items() ])});'