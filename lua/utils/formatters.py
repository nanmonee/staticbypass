def bytes_to_lua(bytestring: bytes, name: str) -> str:
    return f'local {name} = {{ {','.join([hex(value) for value in bytestring])} }}'

def str_to_lua(string: str, name: str) -> str:
    return f'local {name} = "{string}"'

def dict_to_lua(dictionary: str, name: str) -> str:
    return f'local {name} = {{ {','.join([f'{key} = {value}' for key, value in dictionary.items()])}  }}'
