from sg_send_deploy.lambda__watchdog.Watchdog__Service import Watchdog__Service


def run(event, context=None):
    """Lambda handler for the Watchdog, triggered by EventBridge schedule."""
    watchdog = Watchdog__Service()
    return watchdog.check_and_stop_idle()
