from pathlib import Path

path__sg_send_deploy = Path(__file__).parent.parent
version_file         = path__sg_send_deploy / 'version'
version__sg_send_deploy = version_file.read_text().strip() if version_file.exists() else 'v0.1.0'
