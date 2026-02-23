from mangum import Mangum

from sg_send_deploy.lambda__deploy.Deploy__Fast_API import Deploy__Fast_API

deploy_fast_api = Deploy__Fast_API()
deploy_fast_api.setup()

app     = deploy_fast_api.app()
handler = Mangum(app)
