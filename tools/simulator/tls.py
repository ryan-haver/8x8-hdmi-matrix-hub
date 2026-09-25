"""Self-signed certificate for the simulator's HTTPS listener.

The real BK-808 serves a self-signed certificate too, which is why the hub
defaults to ``OREI_VERIFY_SSL=false``. Generated once per process with the
``cryptography`` package (a ``dev`` extra) and cached in a temp directory.
"""

from __future__ import annotations

import datetime
import ipaddress
import ssl
import tempfile
from pathlib import Path

_CACHE: dict[tuple[str, ...], tuple[Path, Path]] = {}


def generate_self_signed(hosts: tuple[str, ...] = ("localhost", "127.0.0.1")) -> tuple[Path, Path]:
    """Return ``(cert_path, key_path)`` for a fresh EC P-256 self-signed cert."""
    if hosts in _CACHE:
        return _CACHE[hosts]
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.x509.oid import NameOID
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "The simulator needs the 'cryptography' package for HTTPS "
            "(pip install -e .[dev]); or run it with --no-tls and point the hub at plain HTTP."
        ) from exc

    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "BK-808 simulator")])
    alt_names: list[x509.GeneralName] = []
    for host in hosts:
        try:
            alt_names.append(x509.IPAddress(ipaddress.ip_address(host)))
        except ValueError:
            alt_names.append(x509.DNSName(host))
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
        .sign(key, hashes.SHA256())
    )
    directory = Path(tempfile.mkdtemp(prefix="bk808-sim-tls-"))
    cert_path = directory / "cert.pem"
    key_path = directory / "key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    _CACHE[hosts] = (cert_path, key_path)
    return cert_path, key_path


def server_ssl_context(hosts: tuple[str, ...] = ("localhost", "127.0.0.1")) -> ssl.SSLContext:
    cert_path, key_path = generate_self_signed(hosts)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(cert_path), str(key_path))
    return ctx
