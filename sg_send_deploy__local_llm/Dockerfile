FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir osbot-utils osbot-fast-api osbot-fast-api-serverless memory-fs httpx "uvicorn[standard]" python-multipart

COPY sg_send_deploy_local_llm/ sg_send_deploy_local_llm/
COPY static/ static/

RUN mkdir -p /app/data/sessions

EXPOSE 8080

CMD ["uvicorn", "sg_send_deploy_local_llm.server:app", "--host", "0.0.0.0", "--port", "8080"]
