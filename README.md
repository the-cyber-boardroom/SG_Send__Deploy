# SG_Send__Deploy

![release-v0.1.9](https://img.shields.io/badge/release-v0.1.0-blue)

Infrastructure management and ephemeral deployment for SGraph Send data rooms.

## What This Does

- **EC2 Management API** -- Create, list, start, stop, terminate EC2 instances via FastAPI
- **Budget Controls** -- Max 5 instances, $10/day cap, idle auto-terminate
- **Audit Trail** -- Hash-chained, tamper-evident logs for all EC2 operations
- **AMI Builder** -- Base image with SG/Send pre-installed (Phase 2)
- **Config Push** -- Push branding, directory, encrypted files to running instances (Phase 3)
- **DNS Routing** -- `{room-name}.send.sgraph.ai` subdomain routing (Phase 4)
- **Fleet Management** -- Data room lifecycle orchestration (Phase 4-5)

## Architecture

```
Deploy Management Lambda  -->  EC2 Instances (data rooms)  -->  DNS routing
     (this repo)                   (App__Send AMI)           ({name}.send.sgraph.ai)
```

## Quick Start

```bash
pip install -r requirements.txt
python -m pytest tests/unit/ -v
```

## Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.12 |
| Web framework | FastAPI via osbot-fast-api-serverless |
| AWS operations | osbot-aws (never raw boto3) |
| SSH client | paramiko |
| Type system | Type_Safe from osbot-utils (never Pydantic) |
| Testing | pytest (no mocks, no patches) |

## Links

- [SG/Send Application](https://send.sgraph.ai)
- [App__Send Repository](https://github.com/the-cyber-boardroom/SGraph-AI__App__Send)
