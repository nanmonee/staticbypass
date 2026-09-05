import random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.asn1 import DerSequence
from Crypto.Util import number
from Crypto.Hash import SHA256
from base64 import standard_b64encode
import string
from cs.utils.formatters import str_to_cs


class RSAEncrypt:

    def __init__(self, arguments: dict) -> None:
        self.key = RSA.generate(2048)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.private_key = self.privKeyXML(self.key.export_key(format='DER', pkcs=1))

    def imports(self) -> list[str]:
        return ["using System.Security.Cryptography;"]

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        cipher = PKCS1_OAEP.new(self.key.public_key())
        self.plaintextLength = len(plaintext)
        ciphertext = b''
        count = 0
        for i in range(0, len(plaintext), 190):
            ciphertext += cipher.encrypt(plaintext[i:i+190])
            count += 1
        return ciphertext

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
        public static byte[] {self.name}(byte[] ciphertext)
        {{
            {str_to_cs(self.private_key, 'key')}

            byte [] plaintext = new byte[{self.plaintextLength}];
            RSA rsa = RSA.Create();

            rsa.FromXmlString(key);

            for (int i=0; i<ciphertext.Length; i+=256){{
                byte[] subset = ciphertext.Skip(i).Take(256).ToArray();
                byte[] decryptedBytes = rsa.Decrypt(subset, RSAEncryptionPadding.OaepSHA1);
                Array.Copy(decryptedBytes, 0, plaintext, (i/256)*190, decryptedBytes.Length);
            }}

            return plaintext;
        }}
"""
    
    def privKeyXML(self, pem):
        keyDer = DerSequence()
        keyDer.decode(pem)
        xml  = b'<RSAKeyValue>'
        xml += b'<Modulus>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[1], blocksize=256))
        xml += b'</Modulus>'
        xml += b'<Exponent>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[2]))
        xml += b'</Exponent>'
        xml += b'<D>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[3], blocksize=256))
        xml += b'</D>'
        xml += b'<P>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[4], blocksize=128))
        xml += b'</P>'
        xml += b'<Q>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[5], blocksize=128))
        xml += b'</Q>'
        xml += b'<DP>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[6], blocksize=128))
        xml += b'</DP>'
        xml += b'<DQ>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[7], blocksize=128))
        xml += b'</DQ>'
        xml += b'<InverseQ>'
        xml += standard_b64encode(number.long_to_bytes(keyDer[8], blocksize=128))
        xml += b'</InverseQ>'
        xml += b'</RSAKeyValue>'
        return xml.decode()