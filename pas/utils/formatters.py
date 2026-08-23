def bytes_to_pas(bytestring: bytes, name: str) -> str:
    return f'{name} := TBytes.Create({','.join([f"${x:x}" for x in bytestring])});'

def str_to_pas(string: str, name: str) -> str:
    return f'{name} := \'{string}\';'

def list_to_pas(itemList: list[str], name: str) -> str:
    return f'{name} := TStringArray.Create({','.join([f"'{x}'" for x in itemList])});'

def dict_to_pas(dictionary: dict[str, int], name: str) -> str:
    codeblock = f'{name} := TStringIntMap.Create;\n'
    for key, value in dictionary.items():
        codeblock += f'{name}.Add(\'{key}\', {value});\n'
    return codeblock