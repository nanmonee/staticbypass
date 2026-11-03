def bytes_to_lua(bytestring: bytes, name: str) -> str:
    formatted = f'local {name}Array = c.Array("C", 1, {len(bytestring)})\n'
    formatted += f'local {name} = {name}Array {{ {','.join([hex(value) for value in bytestring])} }}'
    return formatted
