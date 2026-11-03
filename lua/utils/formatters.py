def bytes_to_lua(bytestring: bytes, name: str) -> str:
    return f'local {name} = {{ {','.join([hex(value) for value in bytestring])} }}'
