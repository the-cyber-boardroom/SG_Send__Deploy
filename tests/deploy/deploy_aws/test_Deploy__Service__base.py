import pytest
from osbot_utils.utils.Misc                                               import list_set
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API        import DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK
from sg_send_deploy.lambda__deploy.deploy__config                         import SG_SEND__DEPLOY__LAMBDA_DEPENDENCIES
from sg_send_deploy.lambda__deploy.lambda_function.deploy.Deploy__Service import Deploy__Service


class test_Deploy__Service__base():
    stage: str = None

    @classmethod
    def setUpClass(cls):
        if cls.stage is None:
            pytest.skip("Can't run when 'stage' class variable is not set")
        cls.deploy_fast_api = Deploy__Service(stage=cls.stage)
        with cls.deploy_fast_api as _:
            if _.aws_config.aws_configured() is False:
                pytest.skip("this test needs valid AWS credentials")

    def test_1__check_stages(self):
        assert self.deploy_fast_api.stage == self.stage

    def test_2__upload_dependencies(self):
        upload_results = self.deploy_fast_api.upload_lambda_dependencies_to_s3()
        assert list_set(upload_results) == SG_SEND__DEPLOY__LAMBDA_DEPENDENCIES

    def test_3__create(self):
        assert self.deploy_fast_api.create() is True
        self.deploy_fast_api.lambda_function().configuration_update(Runtime='python3.13')
        self.deploy_fast_api.lambda_function().wait_for_function_update_to_complete()

    def test_4__invoke(self):
        assert self.deploy_fast_api.invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK

    def test_5__invoke__function_url(self):
        assert self.deploy_fast_api.invoke__function_url('/info/health') == {'status': 'ok'}
