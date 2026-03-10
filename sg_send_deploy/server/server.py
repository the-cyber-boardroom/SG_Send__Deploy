import os

from sg_send_deploy.lambda__deploy.Fast_API__SG_Send__Deploy import Fast_API__SG_Send__Deploy
from sg_send_deploy.server.ssl_certs                         import generate_self_signed_cert


def create_app():
    """Create and configure the FastAPI app for EC2 deployment."""
    fast_api = Fast_API__SG_Send__Deploy()
    fast_api.setup()
    return fast_api.app()


def run_server():
    """Run the FastAPI server with self-signed SSL on EC2."""
    import uvicorn

    host = os.environ.get('DEPLOY_HOST', '0.0.0.0')
    port = int(os.environ.get('DEPLOY_PORT', '443'))

    ssl_config = generate_self_signed_cert()

    uvicorn.run(create_app(),
                host     = host                    ,
                port     = port                    ,
                ssl_certfile = ssl_config['cert_file'] ,
                ssl_keyfile  = ssl_config['key_file']  )


if __name__ == '__main__':
    run_server()
