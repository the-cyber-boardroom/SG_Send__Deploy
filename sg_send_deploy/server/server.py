import os

from sg_send_deploy.ec2.actions.Service__EC2_Instances             import Service__EC2_Instances
from sg_send_deploy.ec2.actions.Service__EC2_SSH                   import Service__EC2_SSH
from sg_send_deploy.ec2.routes.Routes__EC2_SSH                     import Routes__EC2_SSH
from sg_send_deploy.lambda__deploy.Fast_API__SG_Send__Deploy       import Fast_API__SG_Send__Deploy


def create_app():
    """Create the FastAPI app for local development.

    Uses Fast_API__SG_Send__Deploy (extends Serverless__Fast_API)
    which provides API key middleware, CORS, and standard routes.
    Uses EC2_Provider__Twin by default (no AWS needed).
    Set USE_AWS_PROVIDER=true to use real AWS."""

    use_aws = os.environ.get('USE_AWS_PROVIDER', '').lower() == 'true'

    if use_aws:
        service     = Service__EC2_Instances()
        service_ssh = Service__EC2_SSH()
    else:
        from sg_send_deploy.ec2.providers.EC2_Provider__Twin     import EC2_Provider__Twin
        from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet import Type__Twin__EC2__Fleet
        from sg_send_deploy.twins.ssh.SSH__Execute__Twin         import SSH__Execute__Twin
        fleet        = Type__Twin__EC2__Fleet()
        provider     = EC2_Provider__Twin(fleet=fleet)
        service      = Service__EC2_Instances(ec2_provider=provider)
        ssh_twin     = SSH__Execute__Twin()
        service_ssh  = Service__EC2_SSH(ssh_execute=ssh_twin)

    fast_api = Fast_API__SG_Send__Deploy(service_instances=service)
    fast_api.setup()

    app = fast_api.app()

    # SSH routes (not yet in Fast_API__SG_Send__Deploy)
    routes_ssh = Routes__EC2_SSH(app=app, service_ssh=service_ssh)
    routes_ssh.setup()

    return app


def run_server():
    """Run the FastAPI server locally."""
    import uvicorn

    host    = os.environ.get('DEPLOY_HOST', '0.0.0.0')
    port    = int(os.environ.get('DEPLOY_PORT', '10062'))
    use_ssl = os.environ.get('DEPLOY_USE_SSL', '').lower() == 'true'

    kwargs = dict(host      = host ,
                  port      = port ,
                  log_level = 'info')

    if use_ssl:
        from sg_send_deploy.server.ssl_certs import generate_self_signed_cert
        ssl_config = generate_self_signed_cert()
        kwargs['ssl_certfile'] = ssl_config['cert_file']
        kwargs['ssl_keyfile']  = ssl_config['key_file']

    uvicorn.run(create_app(), **kwargs)


if __name__ == '__main__':
    run_server()
