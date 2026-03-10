from unittest import TestCase

from sg_send_deploy.docker.Lambda_Docker__SG_Send__Deploy import Lambda_Docker__SG_Send__Deploy, IMAGE_NAME


class Test__Lambda_Docker__SG_Send__Deploy(TestCase):

    def test_image_name(self):
        docker = Lambda_Docker__SG_Send__Deploy()
        assert docker.image_name == IMAGE_NAME

    def test_dockerfile_path__exists(self):
        docker = Lambda_Docker__SG_Send__Deploy()
        path = docker.dockerfile_path()
        assert 'images/sg-send-deploy' in path

    def test_ecr_repository_name(self):
        docker = Lambda_Docker__SG_Send__Deploy()
        assert docker.ecr_repository_name() == IMAGE_NAME
