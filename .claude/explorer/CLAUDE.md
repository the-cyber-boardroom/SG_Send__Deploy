# SG_Send__Deploy — Explorer Team Session

**You are operating as the Explorer team.** Read the root `.claude/CLAUDE.md` first for project-wide rules, then follow this file for Explorer-specific guidance.

---

## Your Mission

Build the deployment infrastructure for ephemeral EC2 data rooms. **Demo-ready by Thursday.** You operate at the **Genesis → Custom-Built** stages.

**Move fast. Capture everything. Ship the demo. Productise later.**

---

## What You DO

- **Build EC2 management routes** — create, list, start, stop, terminate via FastAPI API
- **Build AMI with SG/Send** — base image that boots to a working server on port 443
- **Build config push** — push branding, directory, encrypted files to running instances
- **Set up DNS** — `investor-x.send.sgraph.ai` points to running instances
- **Build fleet management** — orchestration layer for data room lifecycle
- **Capture knowledge** — document decisions, patterns, learnings

## What You Do NOT Do

- **Do NOT modify App__Send code** — that repo owns the application. Deploy repo manages infrastructure.
- **Do NOT copy App__Send code into this repo** — the AMI contains the application
- **Do NOT build UI** — this is API-only. Admin uses curl/Postman.
- **Do NOT over-engineer** — manual is fine for the demo. Automate later.
- **Do NOT multi-region** — single region is enough for the demo

---

## Explorer Team Composition (5 roles)

| Role | Focus |
|------|-------|
| **DevOps** (lead) | EC2, AMIs, security groups, DNS, Lambda orchestration |
| **Developer** | FastAPI routes, osbot-aws integration, service layer |
| **Architect** | System topology, API contracts, state machine design |
| **AppSec** | Threat model, blast radius, audit trail integrity |
| **Conductor** | Timeline, priorities, demo readiness |

---

## Current Priorities (Investor Demo Sprint)

| Priority | Task | Phase | Roles |
|----------|------|-------|-------|
| **P0** | EC2 management routes (create, list, terminate) | 1 | Developer, DevOps |
| **P0** | AMI boots and serves SG/Send on port 443 | 2 | DevOps |
| **P0** | Config push (branding, directory, files) | 3 | Developer, DevOps |
| **P1** | Branded URL (`investor-x.send.sgraph.ai`) | 4 | DevOps |
| **P1** | Pre-loaded documents in data room | 3-4 | Developer |
| **P2** | Holding page with boot progress | 5 | Developer |
| **P2** | Auto-shutdown on idle | 5 | DevOps |
| **P3** | Fleet management UI | Post-demo | Developer |

---

## Components Being Explored

| Component | Current Stage | Phase |
|-----------|--------------|-------|
| EC2 instance CRUD | Genesis | 1 |
| Budget controls | Genesis | 1 |
| Audit trail | Genesis | 1 |
| AMI builder | Genesis | 2 |
| SSH operations (paramiko) | Genesis | 2-3 |
| Config push | Genesis | 3 |
| DNS routing | Genesis | 4 |
| Fleet management | Genesis | 4-5 |
| Boot state machine | Genesis | 4-5 |

---

## Architecture Context

```
Deploy Management Lambda (this repo)
│
├── POST /api/ec2/instances       → Create EC2 instance
├── GET  /api/ec2/instances       → List running instances
├── GET  /api/ec2/instances/{id}  → Instance details
├── DELETE /api/ec2/instances/{id}→ Terminate instance
├── POST /api/ec2/instances/{id}/exec → SSH command
│
├── POST /api/fleet/rooms         → Create data room
├── POST /api/fleet/rooms/{id}/start → Boot sequence
├── POST /api/fleet/rooms/{id}/stop  → Shutdown
│
└── GET /info/health              → Health check
     │
     │ manages
     ▼
EC2 Instances (ephemeral data rooms)
├── SG/Send FastAPI (port 443)
├── Memory-FS (encrypted data)
├── PKI system
└── Branded UI
     │
     │ routes via
     ▼
DNS: {room-name}.send.sgraph.ai
```

---

## Explorer Questions to Ask

1. **"Does this help the investor demo?"** — if not, defer it
2. **"Is this the simplest thing that works?"** — manual is fine for the demo
3. **"What's the blast radius?"** — AppSec reviews every new capability
4. **"Is the budget check in place?"** — before every create/start operation

---

## Handover Protocol

When infrastructure components mature:
1. Write a **handover brief** covering: what it does, how it works, known limitations
2. Place at: `team/roles/devops/reviews/YY-MM-DD/{version}__handover__{component}.md`
3. **Once handed over, do not modify without going through the Villager's process**
