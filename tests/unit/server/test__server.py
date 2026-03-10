import os
from unittest import TestCase

from sg_send_deploy.server.ssl_certs import generate_self_signed_cert


class Test__Server__Module(TestCase):

    def test_ssl_certs_module_importable(self):
        assert callable(generate_self_signed_cert)

    def test_server_module_exists(self):
        import sg_send_deploy.server
        assert sg_send_deploy.server is not None
