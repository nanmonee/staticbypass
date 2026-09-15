import random
import string

class avx2:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return ['-mavx512cd']

    def transformer(self, shellcodestring: str) -> str:
        return f'{self.name}();\n\t' + shellcodestring

    def codeblock(self) -> str:
        return f"""
void {self.name}()
{{
    __m256i a = _mm256_set1_epi32(10);
}}
"""