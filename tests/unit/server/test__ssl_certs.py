import os
import tempfile
from unittest import TestCase

from sg_send_deploy.server.ssl_certs import generate_self_signed_cert


class Test__SSL_Certs(TestCase):

    def test_generate_self_signed_cert__creates_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = generate_self_signed_cert(cert_dir=tmp_dir)

            assert result['created']   is True
            assert os.path.exists(result['cert_file'])
            assert os.path.exists(result['key_file'])
            assert result['cert_file'].endswith('server.crt')
            assert result['key_file'].endswith('server.key')

    def test_generate_self_signed_cert__reuses_existing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            first  = generate_self_signed_cert(cert_dir=tmp_dir)
            second = generate_self_signed_cert(cert_dir=tmp_dir)

            assert first['created']  is True
            assert second['created'] is False
            assert first['cert_file'] == second['cert_file']
