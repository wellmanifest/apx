---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "minimal-demo-spec",
  "kind": "reference",
  "version": 1,
  "title": "Specyfikacja aplikacji Minimal Demo APX",
  "status": "implemented",
  "owner": "wellmanifest/apx",
  "created": "2026-10-05",
  "updated": "2026-10-05",
  "review_after": "2026-10-19",
  "source_revision": "working-tree",
  "affected_repositories": ["wellmanifest/apx"],
  "evidence": ["repo://wellmanifest/apx/examples/minimal-app/apx.yaml"]
}
---

# Specyfikacja aplikacji Minimal Demo APX

<!-- docs:section purpose -->
## Cel

Wzorcowa implementacja autonomicznej paczki aplikacji APX zgodnie z `urn:wellmanifest:spec:apx:v1`.

<!-- docs:section scope -->
## Zakres

Obejmuje serwer HTTP API (port 8090), kontrakt CQRS, rejestr zdarzeń JSONL oraz metadane SSoT.

<!-- docs:section evidence -->
## Dowody

- Manifest APX: [`apx.yaml`](../apx.yaml)
- Kontrakt SSoT: [`../ssot.yaml`](../ssot.yaml)
- Podręcznik CQRS: [`USER_MANUAL.md`](./USER_MANUAL.md)

<!-- docs:section content -->
## Zawartość

Aplikacja operuje w izolowanym procesie z deterministycznym punktem kontrolnym `/health`.

<!-- docs:section limitations -->
## Ograniczenia

Działa w lokalnej pętli zwrotnej (127.0.0.1) w zaufanym środowisku hosta.

<!-- docs:section next_actions -->
## Kolejne kroki

Rozbudowa endpointów biznesowych w module `server.py`.
