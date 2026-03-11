import os

from fastapi import FastAPI

from sg_send_deploy.ec2.actions.Service__EC2_Instances   import Service__EC2_Instances
from sg_send_deploy.ec2.routes.Routes__EC2_Instances     import Routes__EC2_Instances
from sg_send_deploy.server.routes.Routes__Status         import Routes__Status
from sg_send_deploy.utils.Version                        import version__sg_send_deploy


def create_app():
    """Create the FastAPI app for local development.

    Uses EC2_Provider__Twin by default (no AWS needed).
    Set USE_AWS_PROVIDER=true to use real AWS."""

    use_aws = os.environ.get('USE_AWS_PROVIDER', '').lower() == 'true'

    if use_aws:
        service = Service__EC2_Instances()                              # defaults to EC2_Provider__AWS
    else:
        from sg_send_deploy.ec2.providers.EC2_Provider__Twin     import EC2_Provider__Twin
        from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet import Type__Twin__EC2__Fleet
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        service  = Service__EC2_Instances(ec2_provider=provider)

    app = FastAPI(title   = 'SG/Send Deploy'                                                     ,
                  version = version__sg_send_deploy                                               ,
                  description = 'Infrastructure management for SGraph Send ephemeral data rooms'  )

    routes_ec2    = Routes__EC2_Instances(app=app, service_instances=service)
    routes_status = Routes__Status(app=app, ec2_provider=service.ec2_provider)
    routes_ec2.setup()
    routes_status.setup()

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
