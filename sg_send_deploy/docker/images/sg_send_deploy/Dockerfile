FROM public.ecr.aws/lambda/python:3.12-arm64

# Install openssh-client for SSH and SCP (used by osbot-utils SSH helpers)
RUN dnf install -y openssh-clients && dnf clean all

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy application code
COPY sg_send_deploy/ ${LAMBDA_TASK_ROOT}/sg_send_deploy/

# Set the handler
CMD ["sg_send_deploy.lambda__deploy.handler.run"]
