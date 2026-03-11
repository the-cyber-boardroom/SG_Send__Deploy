#!/bin/bash
# Run the SG/Send Deploy FastAPI server locally.
#
# Usage:
#   ./scripts/run-locally.sh              # twins (no AWS, in-memory)
#   ./scripts/run-locally.sh --aws        # real AWS provider
#   ./scripts/run-locally.sh --ssl        # with self-signed SSL
#
# The server starts on http://localhost:10062
# Docs at http://localhost:10062/docs

PORT=10065

# Load environment variables from .local-server.env if it exists
if [ -f .local-server.env ]; then
    echo "Loading environment variables from .local-server.env..."
    export $(cat .local-server.env | grep -v '^#' | grep -v '^[[:space:]]*$' | xargs)
    echo "✓ Environment variables loaded"
fi

# Parse flags
for arg in "$@"; do
    case $arg in
        --aws)
            export USE_AWS_PROVIDER=true
            echo "✓ Using AWS provider (real EC2 calls)"
            ;;
        --ssl)
            export DEPLOY_USE_SSL=true
            echo "✓ SSL enabled (self-signed cert)"
            ;;
    esac
done

export DEPLOY_PORT=$PORT

if [ "$USE_AWS_PROVIDER" = "true" ]; then
    echo "Mode:     AWS (real EC2 instances)"
    if [ -z "$AWS_ACCESS_KEY_ID" ]; then
        echo "⚠️  Warning: AWS_ACCESS_KEY_ID not set"
        echo "   Set credentials in .local-server.env or export them"
    fi
else
    echo "Mode:     Local (in-memory twins, no AWS needed)"
fi

PROTOCOL="http"
if [ "$DEPLOY_USE_SSL" = "true" ]; then
    PROTOCOL="https"
fi
echo "Server:   ${PROTOCOL}://localhost:${PORT}"
echo "Docs:     ${PROTOCOL}://localhost:${PORT}/docs"
echo ""

python -m uvicorn sg_send_deploy.server.server:create_app --factory --reload --host 0.0.0.0 --port $PORT \
    --log-level info \
    --timeout-graceful-shutdown 0
