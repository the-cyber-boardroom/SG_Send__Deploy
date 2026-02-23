---
layout: default
title: Home
permalink: /
---

# SG/Send Deploy

Infrastructure management and ephemeral deployment for SGraph Send data rooms.

## What This Does

- **EC2 Management** — Create, list, start, stop, terminate instances via FastAPI API
- **AMI Builder** — Base image with SG/Send pre-installed, boots to server on port 443
- **Config Push** — Push branding, directory, encrypted files to running instances
- **DNS Routing** — `{room-name}.send.sgraph.ai` points to running instances
- **Fleet Management** — Orchestration layer for data room lifecycle

## Architecture

```
Deploy Management Lambda  →  EC2 Instances (data rooms)  →  DNS routing
```

## Links

- [SG/Send Application](https://send.sgraph.ai)
- [Source Code](https://github.com/the-cyber-boardroom/SG_Send__Deploy)
