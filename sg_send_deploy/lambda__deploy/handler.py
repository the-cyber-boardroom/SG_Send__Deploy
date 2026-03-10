import os

if os.getenv('AWS_REGION'):
    from osbot_aws.aws.lambda_.boto3__lambda              import load_dependencies
    from sg_send_deploy.lambda__deploy.deploy__config     import SG_SEND__DEPLOY__LAMBDA_DEPENDENCIES
    load_dependencies(SG_SEND__DEPLOY__LAMBDA_DEPENDENCIES)

    def clear_osbot_modules():
        import sys
        for module in list(sys.modules):
            if module.startswith('osbot_aws'):
                del sys.modules[module]
    clear_osbot_modules()

error = handler = app = None

try:
    from sg_send_deploy.lambda__deploy.Fast_API__SG_Send__Deploy import Fast_API__SG_Send__Deploy
    with Fast_API__SG_Send__Deploy() as _:
        _.setup()
        handler = _.handler()
        app     = _.app()
except Exception as exc:
    if os.getenv('AWS_LAMBDA_FUNCTION_NAME') is None:
        raise
    error = f'CRITICAL ERROR: Failed to start service:\n\n{type(exc).__name__}: {exc}'

def run(event, context=None):
    if error:
        return error
    return handler(event, context)
