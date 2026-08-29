import json

def bytes_to_nim(bytestring: bytes, name: str) -> str:
    return f'var {name} = @[byte {','.join([f"0x{x:02X}" for x in bytestring])}];'

def str_to_nim(string: str, name: str) -> str:
    return f'var {name} = "{string}"'

def list_to_nim(itemList: list[str], name: str) -> str:
    return f'var {name} = @[{','.join([f'"{x}"' for x in itemList])}]'

def dict_to_nim(dictionary: dict[str, int], name: str) -> str:
    return f'var {name} = {json.dumps(dictionary)}.toTable'