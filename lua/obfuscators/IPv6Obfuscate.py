import random
import string

class IPv6Obfuscate:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> list[str]:
        encoded = []
        self.size = 0
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(':'.join([ f'{chunk[n]:02x}{chunk[n+1]:02x}' for n in range(0, 16, 2)]))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encoded)
    local j = 0
    decoded = {{}}
    for i, value in ipairs(encoded) do
        j = 0
        for hexbyte in string.gmatch(value, "%x+") do
            decoded[(i-1)*16 + j*2 + 1] = tonumber(hexbyte, 16) >> 8 & 255
            decoded[(i-1)*16 + j*2 + 1 + 1] = tonumber(hexbyte, 16) & 255
            j = j + 1
        end
    end
    return decoded
end
"""