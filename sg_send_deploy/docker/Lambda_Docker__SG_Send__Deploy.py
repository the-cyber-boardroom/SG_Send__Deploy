import os

from osbot_aws.AWS_Config                       import AWS_Config
from osbot_aws.apis.ECR                         import ECR
from osbot_utils.type_safe.Type_Safe            import Type_Safe
from osbot_utils.utils.Files                    import path_combine


IMAGE_NAME  = 'sg-send-deploy'
IMAGE_TAG   = 'latest'


class Lambda_Docker__SG_Send__Deploy(Type_Safe):
    """Local helper for building and pushing the Lambda Docker image to ECR.
    Uses osbot-aws ECR for registry operations.
    Will be refactored to osbot-aws once confirmed working."""

    image_name : str = IMAGE_NAME
    image_tag  : str = IMAGE_TAG
    ecr        : ECR
    aws_config : AWS_Config

    def dockerfile_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), 'images', self.image_name)

    def ecr_repository_name(self) -> str:
        return self.image_name

    def full_image_uri(self) -> str:
        account_id = self.aws_config.aws_session_account_id()
        region     = self.aws_config.aws_session_region_name()
        return f'{account_id}.dkr.ecr.{region}.amazonaws.com/{self.image_name}:{self.image_tag}'

    def ensure_repository(self) -> dict:
        name = self.ecr_repository_name()
        if self.ecr.repository_exists(name):
            return dict(status='exists', repository=name)
        result = self.ecr.repository_create(name)
        return dict(status='created', repository=name, details=result)

    def ecr_login_command(self) -> str:
        account_id = self.aws_config.aws_session_account_id()
        region     = self.aws_config.aws_session_region_name()
        return (f'aws ecr get-login-password --region {region} | '
                f'docker login --username AWS --password-stdin '
                f'{account_id}.dkr.ecr.{region}.amazonaws.com')

    def build_command(self) -> str:
        return f'docker build -t {self.full_image_uri()} {self.dockerfile_path()}'

    def push_command(self) -> str:
        return f'docker push {self.full_image_uri()}'

    def info(self) -> dict:
        return dict(image_name      = self.image_name               ,
                    image_tag       = self.image_tag                 ,
                    full_image_uri  = self.full_image_uri()          ,
                    dockerfile_path = self.dockerfile_path()         ,
                    repository      = self.ecr_repository_name()     )
