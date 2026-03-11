import os

from fastapi           import FastAPI
from starlette.staticfiles  import StaticFiles
from starlette.responses    import RedirectResponse

from sg_send_deploy.ec2.actions.Service__EC2_Instances import Service__EC2_Instances
from sg_send_deploy.ec2.actions.Service__EC2_SSH       import Service__EC2_SSH
from sg_send_deploy.ec2.routes.Routes__EC2_Instances   import Routes__EC2_Instances
from sg_send_deploy.ec2.routes.Routes__EC2_SSH         import Routes__EC2_SSH
from sg_send_deploy.server.routes.Routes__Status       import Routes__Status
from sg_send_deploy.utils.Version                      import version__sg_send_deploy


def create_app():
    """Create the FastAPI app for local development.

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

    app = FastAPI(title   = 'SG/Send Deploy'                                                     ,
                  version = version__sg_send_deploy                                               ,
                  description = 'Infrastructure management for SGraph Send ephemeral data rooms'  )

    # EC2 instance routes
    routes_ec2    = Routes__EC2_Instances(app=app, service_instances=service)
    routes_ec2.setup()

    # SSH routes
    routes_ssh    = Routes__EC2_SSH(app=app, service_ssh=service_ssh)
    routes_ssh.setup()

    # Deploy status
    routes_status = Routes__Status(app=app, ec2_provider=service.ec2_provider)
    routes_status.setup()

    # Admin UI (static files)
    _mount_admin_ui(app)

    return app


def _mount_admin_ui(app):
    """Mount the admin UI static files at /admin."""
    try:
        import sg_send_deploy__ui__admin
        path_static = sg_send_deploy__ui__admin.path

        app.mount('/admin/static',
                  StaticFiles(directory=path_static),
                  name='admin')

        @app.get('/admin')
        def admin_redirect():
            return RedirectResponse(url='/admin/static/v0/v0.1/v0.1.0/index.html')
    except ImportError:
        pass


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
