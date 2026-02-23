import ssl


def load_ssl_context(cert_file, pkey_file):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, pkey_file)
    return context


def save_ssl_files(cert, pkey):
    import atexit  # noqa:  PLC0415
    import os  # noqa:  PLC0415
    import tempfile  # noqa:  PLC0415

    from cryptography.hazmat.primitives import serialization  # noqa:  PLC0415

    cert_handle, cert_file = tempfile.mkstemp()
    pkey_handle, pkey_file = tempfile.mkstemp()
    atexit.register(os.remove, pkey_file)
    atexit.register(os.remove, cert_file)

    os.write(cert_handle, cert.public_bytes(serialization.Encoding.PEM))
    os.write(
        pkey_handle,
        pkey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )

    os.close(cert_handle)
    os.close(pkey_handle)
    return cert_file, pkey_file


def generate_ssl_pair(host):
    try:
        import datetime  # noqa:  PLC0415

        from cryptography import x509  # noqa:  PLC0415
        from cryptography.hazmat.primitives import hashes  # noqa:  PLC0415
        from cryptography.hazmat.primitives.asymmetric import rsa  # noqa:  PLC0415
        from cryptography.x509.oid import NameOID  # noqa:  PLC0415
    except ImportError:
        msg = "Using ad-hoc certificates requires the cryptography library."
        raise TypeError(msg) from None
    cn = f"*.{host}/CN={host}"
    pkey = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Dummy Certificate"),
            x509.NameAttribute(NameOID.COMMON_NAME, cn),
        ]
    )
    one_day = datetime.timedelta(1, 0, 0)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(pkey.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.today() - one_day)
        .not_valid_after(datetime.datetime.today() + (one_day * 365))
        .add_extension(x509.ExtendedKeyUsage([x509.OID_SERVER_AUTH]), critical=False)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
        .sign(private_key=pkey, algorithm=hashes.SHA256())
    )
    return save_ssl_files(cert, pkey)
