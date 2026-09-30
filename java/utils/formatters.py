def bytes_to_java(bytestring: bytes, name: str) -> str:
    # return f'let {name}= vec![{','.join([f'{hex(val)}' for val in bytestring])}];'
    return f'byte[] {name} = {{ {','.join([f'(byte) {hex(val)}' for val in bytestring])} }};'
