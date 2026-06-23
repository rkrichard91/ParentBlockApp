import os
import datetime
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Definir rutas por defecto en la raíz del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(PROJECT_ROOT, "server.crt")
DEFAULT_KEY = os.path.join(PROJECT_ROOT, "server.key")

def generate_self_signed_cert(cert_path=DEFAULT_CERT, key_path=DEFAULT_KEY):
    """Genera un certificado SSL autofirmado y su clave privada si no existen."""
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return cert_path, key_path
        
    try:
        # 1. Generar la clave privada RSA de 2048 bits
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 2. Configurar detalles de identidad (Subject e Issuer son iguales para autofirmado)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CDMX"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mexico"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ParentalBlock"),
            x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1"),
        ])
        
        # 3. Construir el certificado
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(issuer)
        builder = builder.public_key(private_key.public_key())
        builder = builder.serial_number(x509.random_serial_number())
        
        # Vigencia desde ayer hasta dentro de 10 años
        now = datetime.datetime.now(datetime.timezone.utc)
        builder = builder.not_valid_before(now - datetime.timedelta(days=1))
        builder = builder.not_valid_after(now + datetime.timedelta(days=3650))
        
        # Añadir Nombres Alternativos del Sujeto (SAN) para localhost y 127.0.0.1
        builder = builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        
        # Firmar el certificado con la misma clave privada
        cert = builder.sign(private_key, hashes.SHA256())
        
        # 4. Guardar clave privada en formato PEM
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        # 5. Guardar certificado en formato PEM
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        print(f"Certificado y clave generados con éxito:\n  Cert: {cert_path}\n  Key: {key_path}")
        return cert_path, key_path
        
    except Exception as e:
        print(f"Error generando el certificado SSL autofirmado: {e}")
        raise e
