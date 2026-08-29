import subprocess
import platform
import datetime
import tempfile
import os
import shutil
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class sign:

    def apply(self, outfile: str) -> None:
        # 1. Generate RSA Private Key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # 2. Setup Certificate Authority Details (Subject and Issuer)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Redmond"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Microsoft Corporation"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Microsoft Corporation"),
        ])

        # 3. Build the Self-Signed Certificate
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
            )
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        keytf, keyfilename = tempfile.mkstemp()
        certtf, certfilename = tempfile.mkstemp()
        outtf, outfilename = tempfile.mkstemp()

        # 4. Write Private Key to 'server.key'
        with os.fdopen(keytf, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(), # Use BestAvailableEncryption(b"password") to password-protect
                )
            )

        # 5. Write Certificate to 'server.crt'
        with os.fdopen(certtf, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

        if platform.system() == 'Linux':
            result = subprocess.run(['osslsigncode', 'sign', '-certs', certfilename, '-key', keyfilename, '-in', outfile, '-out', f'{tempfile.gettempdir()}/{outfile}' ])
            shutil.move(f'{tempfile.gettempdir()}/{outfile}', outfile)
            os.unlink(keyfilename)
            os.unlink(certfilename)
