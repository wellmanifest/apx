# Wellmanifest Specification: Autonomous Application Pack (APX) Composition Standard

- **Standard ID**: `urn:wellmanifest:spec:apx:v1`
- **Standard**: `wellmanifest/apx`
- **Revision**: `1.0.0`
- **Status**: `Normative Specification`
- **Date**: `2026-10-05`
- **Governance**: `wellmanifest/new-project`

---

## 1. Executive Summary & Purpose

Autonomous developer interfaces, multi-window tiling managers (`willmux`), and distributed actor runtimes (`willman`, `dockuri`) require a lightweight, standardized packaging format for modular applications. Creating a full separate Git repository with complete CI infrastructure for every small utility app causes severe repository sprawl, fragmented configuration, and operational friction.

The **Autonomous Application Pack (APX)** standard solves this by defining a lightweight, composable application bundle format that can run independently as a standalone service or live as a co-located module inside a multi-project repository (`apps/<app_id>`).

### The Zero-Duplication Composition Contract

Crucially, **`wellmanifest/apx` does not reinvent or duplicate foundational engineering contracts**. Instead, it serves as the **Composition Standard**, mandating strict delegation to dedicated, peer Wellmanifest domain standards:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Autonomous Application Pack (APX)                     │
│  apps/<app-id>/                                                             │
│  ├── apx.yaml       ───> [APX Core]       Manifest, Sandbox & Hooks         │
│  ├── ssot.yaml      ───> wellmanifest/ssot        Single Source of Truth    │
│  ├── AGENTS.md      ───> wellmanifest/new-project Policy-as-Code Governance │
│  ├── logger.py      ───> wellmanifest/logs        Event Sourcing & JSONL    │
│  ├── willman.py     ───> wellmanifest/wellman     Signed ExecutionReceipts  │
│  ├── server.py      ───> wellmanifest/uriprocess  Isolated Process Runtime  │
│  └── doc/                                                                   │
│      ├── README.md  ───> wellmanifest/docs        Architectural Document    │
│      └── usermanual ───> wellmanifest/usermanual  CQRS Commands & Queries   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Normative Architectural Rules

### Rule APX-MAN-001: Canonical Manifest (`apx.yaml`)
Every APX application bundle MUST contain a valid `apx.yaml` in its root directory conforming to schema `urn:willapx:manifest:v1` (or `wellmanifest.apx/manifest/v1`).
- **Required fields**: `schema`, `name`, `title`, `version`, `type` (`web` | `cli` | `service`), and `entrypoint`.
- **Sandbox boundaries**: Applications MUST explicitly declare accessed paths in `resources` and required system privileges in `permissions` (`fs:read`, `fs:write`, `net:local`, `net:external`).
- **Orchestration hooks**: Applications integrate with window managers via optional `willmux` metadata (`default_window`, `bezel`, `palette_cmd`) and task queues via optional `willman` metadata (`operation_prefix`).

### Rule APX-COMP-001: Strict Standards Delegation & Zero Duplication
An APX application MUST NOT introduce proprietary schemas or conventions for concerns already governed by canonical Wellmanifest standards. An APX bundle MUST compose the following peer specifications:

| Domain Concern | Canonical Standard | Required Contract in APX Bundle |
| :--- | :--- | :--- |
| **Documentation** | [`wellmanifest/docs`](https://github.com/wellmanifest/docs) | `doc/README.md` conforming to `wellmanifest.docs/document/v1` with required normative comment blocks (`purpose`, `scope`, `evidence`, `content`, `limitations`, `next_actions`). |
| **API & CQRS** | [`wellmanifest/usermanual`](https://github.com/wellmanifest/usermanual) | `doc/USER_MANUAL.md` or modular `doc/usermanual/` conforming to `wellmanifest.usermanual/v1`, strictly separating safe queries (`GET`) from mutating commands (`POST`/`PUT`/`DELETE`). |
| **Audit Logging** | [`wellmanifest/logs`](https://github.com/wellmanifest/logs) | `logger.py` emitting hash-chained or structured JSONL events conforming to `wellmanifest.logs/event/v1` with catalogued `APX-*` diagnostic codes. |
| **Configuration** | [`wellmanifest/ssot`](https://github.com/wellmanifest/ssot) | `ssot.yaml` conforming to `wellmanifest.ssot/v1` declaring immutable network bindings, canonical endpoints, and governance ownership. |
| **Execution Proof** | [`wellmanifest/wellman`](https://github.com/wellmanifest/wellman) | `willman.py` producing cryptographically signed `ExecutionReceipt` structures (`wellmanifest.wellman/receipt/v1`) with SHA-256 digests and resource URNs. |
| **Process Identity** | [`wellmanifest/uriprocess`](https://github.com/wellmanifest/uriprocess) | Addressed via RFC 3986 Process URI (`process://<host>/apps/<app>/<entrypoint>`) and isolated OS process PID. |
| **Conversational UX** | [`wellmanifest/nl-uri-dsl-llm`](https://github.com/wellmanifest/nl-uri-dsl-llm) | Strict separation of raw CLI terminal output from conversational chat; generation of `DecisionCard v1` (`urn:dockuri:decision-card:v1`) for UI action approval. |
| **Governance** | [`wellmanifest/new-project`](https://github.com/wellmanifest/new-project) | `AGENTS.md` policy-as-code: all modifications allocated via tickets (`project/new-ticket.sh`), tested in worktrees, never committed directly to `main`. |

### Rule APX-ISO-001: Process & Port Isolation
1. An APX application MUST run inside its own isolated process boundary.
2. In daemonized mode, runtime PID files MUST be tracked under `.apx/pids/<app>.pid` (or `.willapx/pids/<app>.pid`).
3. Standard output and error streams MUST be piped into dedicated runtime log files (`.apx/logs/<app>.log`) and MUST NOT pollute conversational dialogue streams.
4. TCP service ports MUST default to non-privileged ranges (>1024) and bind strictly to loopback (`127.0.0.1`) unless explicitly configured otherwise via `ssot.yaml`.

### Rule APX-HLT-001: Deterministic Health Probe
Every APX application of type `web` or `service` MUST implement a fast, non-blocking `GET /health` endpoint:
- Status Code: `200 OK`
- Header: `Content-Type: application/json`
- Response Payload:
  ```json
  {
    "status": "ok",
    "app": "<app_name>"
  }
  ```
The health check must execute without external database or cloud network dependencies.

### Rule APX-DRIFT-001: Zero API Drift Verification
The running APX server MUST be continuously auditable by the `CQRSValidator` from `wellmanifest/usermanual`. Every exposed HTTP route must have a corresponding query or command descriptor in `doc/usermanual/`. Any unmapped or drifting endpoint fails conformance verification.

### Rule APX-DOCK-001: Container Packaging Profile (Hermetic Microservice)
To guarantee deterministic execution and cross-node portability without dependency drift, an APX bundle SHOULD provide hermetic container definitions:
1. **Dependency Lock**: `requirements.txt` (or language package manifest) with strictly declared runtime dependencies.
2. **Deterministic Dockerfile**: Minimal base image (e.g. `python:3.11-alpine`), non-root execution (`USER nobody`), explicit `EXPOSE`, and active `HEALTHCHECK` mapped to `/health`.
3. **Service Orchestration (`compose.yml`)**: Declarative service specification with loopback port mapping (`127.0.0.1:<port>:<port>`), resource boundaries (`deploy.resources.limits`), and volume mounts constrained exclusively to paths declared in `apx.yaml` under `resources`.

### Rule APX-SRV-001: Dockuri Process Mapping & Discrete Service Invocation
Every business action declared under `actions` in `apx.yaml` SHOULD be mapped to a discrete Dockuri process descriptor (`dockuri.json` conforming to `format: dockuri/proc-v1`):
1. **Canonical URI**: `proc://<domain>/<app>/<action>/v1`
2. **Schema Contracts**: Typed `input_schema` and `output_schema`.
3. **Execution Backend**: Backend script or container invocation returning an auditable `ExecutionReceipt` (`wellmanifest.wellman/receipt/v1`).

---

## 3. Directory Layout Specification

A comprehensive APX bundle conforms to the following directory layout:

```text
apps/<app-id>/
├── apx.yaml                 # APX Manifest (Rule APX-MAN-001)
├── ssot.yaml                # Single Source of Truth (wellmanifest/ssot)
├── AGENTS.md                # Policy-as-Code governance (wellmanifest/new-project)
├── logger.py                # Structured event logger (wellmanifest/logs)
├── willman.py               # Subactor & ExecutionReceipt (wellmanifest/wellman)
├── server.py                # Process entrypoint & /health route (Rule APX-HLT-001)
├── requirements.txt         # Hermetic package dependencies (Rule APX-DOCK-001)
├── Dockerfile               # Container build definition (Rule APX-DOCK-001)
├── compose.yml              # Service orchestration & sandboxing (Rule APX-DOCK-001)
├── dockuri.json             # Dockuri URI process descriptor (Rule APX-SRV-001)
├── doc/
│   ├── README.md            # Architecture & reference (wellmanifest/docs)
│   └── usermanual/          # CQRS contract (wellmanifest/usermanual)
│       ├── manifest.yaml
│       ├── queries/
│       └── commands/
└── web/                     # Client interface (HTML5 / ES Modules / CSS)
    ├── index.html
    ├── app.js
    └── app.css
```

---

## 4. Policy DSL Projection

Below is the Policy DSL v1 projection of the APX conformance standard:

```dsl
DOCUMENT APX_CONFORMANCE
VERSION 1
LANGUAGE EN
MODE STRICT
PURPOSE "Deterministic conformance rules for Autonomous Application Packs"

RULE APX-MAN-001 TYPE REQUIRED
WHEN APX_APPLICATION_SCANNED
DO REQUIRE FILE_EXISTS "apx.yaml"
DO REQUIRE VALID_SCHEMA "urn:willapx:manifest:v1" OR "wellmanifest.apx/manifest/v1"
DO REQUIRE FIELDS [name, title, version, type, entrypoint]
DO REQUIRE DECLARED_PERMISSIONS
FORBID UNDECLARED_FILESYSTEM_ACCESS

RULE APX-COMP-001 TYPE REQUIRED
WHEN APX_APPLICATION_VALIDATED
DO REQUIRE DELEGATION docs = "wellmanifest/docs" IN "doc/README.md"
DO REQUIRE DELEGATION usermanual = "wellmanifest/usermanual" IN "doc/USER_MANUAL.md" OR "doc/usermanual/"
DO REQUIRE DELEGATION logs = "wellmanifest/logs" IN "logger.py"
DO REQUIRE DELEGATION ssot = "wellmanifest/ssot" IN "ssot.yaml"
DO REQUIRE DELEGATION wellman = "wellmanifest/wellman" IN "willman.py"
FORBID DUPLICATE_STANDARD_DEFINITIONS

RULE APX-HLT-001 TYPE REQUIRED
WHEN APX_APPLICATION_RUNS
DO REQUIRE ENDPOINT "/health" METHOD "GET"
DO REQUIRE HTTP_STATUS 200
DO REQUIRE JSON_BODY status = "ok"

RULE APX-ISO-001 TYPE REQUIRED
WHEN APX_APPLICATION_SPAWNED
DO REQUIRE ISOLATED_PID_FILE
DO REQUIRE ISOLATED_LOG_FILE
FORBID RAW_STREAM_POLLUTION_OF_CHAT_WINDOW
```
