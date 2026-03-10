import os
import subprocess
import tempfile


def generate_self_signed_cert(cert_dir=None):
    """Generate a self-signed SSL certificate for the Deploy EC2 FastAPI server.

    Returns dict with cert_file and key_file paths."""
    if cert_dir is None:
        cert_dir = os.environ.get('DEPLOY_SSL_CERT_DIR', '/tmp/sg-deploy-ssl')

    cert_file = os.path.join(cert_dir, 'server.crt')
    key_file  = os.path.join(cert_dir, 'server.key')

    if os.path.exists(cert_file) and os.path.exists(key_file):
        return dict(cert_file=cert_file, key_file=key_file, created=False)

    os.makedirs(cert_dir, exist_ok=True)

    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
        '-keyout', key_file,
        '-out'   , cert_file,
        '-days'  , '365',
        '-nodes' ,
        '-subj'  , '/CN=sg-deploy.local/O=SGraph/C=US'
    ], check=True, capture_output=True)

    return dict(cert_file=cert_file, key_file=key_file, created=True)
