# SG_Send__Deploy — Agent Guidance

**Read this before starting any task.** This file is the single source of truth for all agents and roles working on SG_Send__Deploy.

---

## MEMORY.md Policy

**Do NOT use MEMORY.md** (the auto-memory at `~/.claude/projects/.../memory/MEMORY.md`). All persistent project knowledge is maintained in the repo itself. If you need to record something, add it to the appropriate location in `team/roles/` or request the Librarian to update the relevant docs.

---

## Project

**SG_Send__Deploy** — infrastructure management and ephemeral deployment for SGraph Send data rooms.

This is a **separate repo** from `App__Send` (the application). This repo manages EC2 instances, AMIs, DNS, and the orchestration that makes ephemeral data rooms possible. The application code lives in `App__Send` and is packaged into AMIs managed by this repo.

**Version file:** `sg_send_deploy/version`

---

## Stack

| Layer | Technology | Rule |
|-------|-----------|------|
| Runtime | Python 3.12 / arm64 | |
| Web framework | FastAPI via `osbot-fast-api-serverless` | Use `Serverless__Fast_API` base class |
| Lambda adapter | Mangum (via osbot-fast-api) | |
| AWS operations | `osbot-aws` | **Never use boto3 directly** |
| SSH client | `paramiko` | Pure Python, Lambda-compatible |
| Type system | `Type_Safe` from `osbot-utils` | **Never use Pydantic** |
| Storage | Memory-FS (`Storage_FS`) for state | Fleet state, audit logs |
| Testing | pytest, in-memory + integration | **No mocks, no patches** |
| CI/CD | GitHub Actions | Test → tag → deploy |

---

## Architecture

```
Deploy Management Lambda
├── /api/ec2/instances          (CRUD for EC2 instances)
├── /api/ec2/instances/{id}/exec (SSH operations via paramiko)
├── /api/ec2/amis               (AMI management)
├── /api/ec2/keypairs           (SSH key pair management)
├── /api/fleet/rooms            (Data room CRUD)
├── /api/fleet/rooms/{id}/start (Boot sequence)
├── /api/fleet/rooms/{id}/stop  (Shutdown + sync)
└── /info/health                (Health check)

     │
     │ manages
     ▼

EC2 Instances (data rooms)
├── SG/Send FastAPI server (port 443)
├── Memory-FS (loaded from S3)
├── PKI system
└── Branded UI

     │
     │ routes to
     ▼

DNS: {room-name}.send.sgraph.ai
```

**One Lambda function** — Deploy management. Manages EC2 instances. No user-facing UI (API-only).

---

## Repo Structure

```
sg_send_deploy/                  # Application code
  ec2/                           # EC2 management
    routes/                      # FastAPI route handlers
    actions/                     # Service classes (business logic)
    schemas/                     # Type_Safe data models
  fleet/                         # Fleet / data room management
    routes/
    actions/
    schemas/
  lambda__deploy/                # The management Lambda
    Deploy__Fast_API.py          # FastAPI app (extends Serverless__Fast_API)
    handler.py                   # Lambda handler (Mangum)
  ami/                           # AMI builder scripts
  utils/                         # Shared utilities (audit trail, auth)

tests/
  unit/                          # Fast, in-memory tests
  integration/                   # Tests that hit real AWS

sg_send_deploy__site/            # Jekyll documentation site
  _config.yml
  Gemfile
  pages/

.claude/                         # Claude Code session configuration
  CLAUDE.md                      # This file
  explorer/CLAUDE.md             # Explorer team session instructions

.github/workflows/               # CI pipelines

team/                            # Team structure
  roles/                         # Role-based review documents
  humans/dinis_cruz/briefs/      # Human briefs (read-only for agents)
```

---

## Key Rules

### Code Patterns

1. **All schemas** use `Type_Safe` (from `osbot-utils`), never Pydantic
2. **All AWS calls** go through `osbot-aws`, never `boto3` directly
3. **All storage** goes through Memory-FS (`Storage_FS`), never direct filesystem or S3 calls
4. **All FastAPI apps** extend `Serverless__Fast_API` from `osbot-fast-api-serverless`
5. **All tests** use real implementations (in-memory Memory-FS), no mocks or patches
6. **Version prefix** on all review/doc files: `{version}__{description}.md`
7. **Routes are thin wrappers** — business logic lives in service classes in `actions/`

### EC2 Security Posture

8. **Port 443 inbound only** — HTTPS. Nothing else.
9. **Zero egress** — EC2 instances are fully isolated. No outbound access.
10. **No IAM role** — instances have no AWS API access.
11. **Data push model** — Lambda pushes config TO instances. Instances never pull.
12. **SSH via paramiko only** — from Lambda, not exposed to internet.

### Budget Controls

13. **Max 5 concurrent instances** — enforced in service layer before every create/start
14. **$10/day spend cap** — checked before instance creation
15. **30-minute idle auto-terminate** — configurable per data room
16. **Budget check before every create/start** — this is a hard requirement

### Audit Trail

17. **Every EC2 operation logged** — create, start, stop, terminate, SSH exec
18. **Hash-chained entries** — each entry includes hash of previous entry (tamper-evident)
19. **Admin identity recorded** — who performed the action
20. **Stored in Memory-FS** — S3 backend for persistence

### Testing

21. **No mocks, no patches** — full stack starts in-memory
22. **Integration tests** marked separately — they hit real AWS
23. **Budget controls tested** with in-memory state

### Git

24. **Default branch:** `dev`
25. **Feature branches** branch from `dev`
26. **Branch naming:** `claude/{description}-{session-id}`
27. **Always push with:** `git push -u origin {branch-name}`

### Human Folders — Read-Only for Agents

28. **`team/humans/dinis_cruz/briefs/` is HUMAN-ONLY.** Agents must NEVER create, modify, or move files into this folder.
29. **Agent session outputs** go to `team/humans/dinis_cruz/claude-code-web/MM/DD/`
30. **Debriefs** go to `team/humans/dinis_cruz/debriefs/MM/DD/`
31. **Role reviews** go to `team/roles/{role}/reviews/YY-MM-DD/`

### File Naming

32. **Review files:** `team/roles/{role}/reviews/YY-MM-DD/{version}__{description}.md`
33. **Debrief files:** `team/humans/dinis_cruz/debriefs/MM/DD/{version}__debrief__{description}.md`
34. **Version** comes from `sg_send_deploy/version`

---

## Role System

5 roles, Explorer team only (this is a new project in Genesis stage):

| Role | Identity | Focus |
|------|----------|-------|
| **DevOps** (lead) | Infrastructure owner | EC2, AMIs, networking, DNS, Lambda |
| **Developer** | API builder | FastAPI routes, osbot-aws integration, services |
| **Architect** | System designer | Topology, API contracts, state machine |
| **AppSec** | Security reviewer | Threat model, blast radius, audit trail |
| **Conductor** | Product owner | Timeline, priorities, demo readiness |

**Dinis Cruz** is the human stakeholder, decision-maker, and project owner. His briefs drive the team's priorities. **The `briefs/` folder is read-only for agents.**

---

## Current State (v0.1.0)

**Phase:** Bootstrap (Phase 0) + EC2 Management Routes (Phase 1)

**Sprint goal:** Investor demo by Thursday/Friday. Build ephemeral EC2 data rooms.

**5-phase plan:**
1. Phase 0: Repo bootstrap, verify osbot-aws, find base AMI
2. Phase 1: EC2 management routes (create, list, terminate)
3. Phase 2: AMI with SG/Send, boots to working server
4. Phase 3: Config push (branding, directory, documents)
5. Phase 4: DNS + live investor data room

---

## Key Documents (Reference)

| Document | Location |
|----------|----------|
| Bootstrap pack | `App__Send/library/sgraph-send/dev_packs/v0.5.33__deploy-ephemeral-ec2-data-rooms/` |
| EC2 routes brief | `App__Send/team/humans/dinis_cruz/briefs/02/21/part-3/v0.5.10__dev-brief__fastapi-ec2-management-routes.md` |
| Architecture brief | `App__Send/team/humans/dinis_cruz/briefs/02/21/part-3/v0.5.10__architecture__github-store-and-ephemeral-compute.md` |
| Data rooms brief | `App__Send/team/humans/dinis_cruz/briefs/02/21/part-3/v0.5.10__product-brief__data-rooms.md` |
| App__Send CLAUDE.md | `App__Send/.claude/CLAUDE.md` |

---

## Integration with App__Send

The AMI is the boundary between the two repos:

```
App__Send code  →  packaged into AMI  →  managed by Deploy repo
```

This repo needs to know:
1. **How to build the AMI** — what to install, how to configure
2. **How to start SG/Send** — the systemd service, the port, the health check endpoint
3. **How to push config** — the admin API endpoints on the running instance

This repo does **not** modify application code. If SG/Send needs a change, that happens in App__Send and a new AMI is built.
