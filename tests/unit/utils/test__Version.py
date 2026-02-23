from unittest import TestCase

from sg_send_deploy.utils.Version import version__sg_send_deploy


class Test__Version(TestCase):

    def test_version_exists(self):
        assert version__sg_send_deploy is not None
        assert version__sg_send_deploy != ''

    def test_version_starts_with_v(self):
        assert version__sg_send_deploy.startswith('v')
