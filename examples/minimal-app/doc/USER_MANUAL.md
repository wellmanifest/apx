---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "minimal-demo-user-manual",
  "kind": "guide",
  "version": 1,
  "title": "Podręcznik CQRS aplikacji Minimal Demo APX",
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

# Podręcznik CQRS aplikacji Minimal Demo APX

<!-- docs:section purpose -->
## Cel

Prezentacja powierzchni API zgodnej ze wzorcem CQRS według standardu `wellmanifest/usermanual`.

<!-- docs:section scope -->
## Zakres

Specyfikacja zapytań (Queries) i poleceń (Commands) aplikacji Minimal Demo APX.

<!-- docs:section evidence -->
## Dowody

Zgodność z manifestem `apx.yaml` i testami live drift.

<!-- docs:section content -->
## Zawartość

### Queries (Odczyt)
- `GET /health`: Kontrola stanu zdrowia aplikacji.
- `GET /api/stats`: Podstawowe statystyki runtime i statusu węzła.

### Commands (Mutacja)
- Akcje biznesowe deklarowane w `apx.yaml` pod kluczem `actions`.

### Zmienne środowiskowe
- `PORT`: Port HTTP serwera (domyślnie `8090`).

<!-- docs:section limitations -->
## Ograniczenia

Brak bezpośredniego zapisu bazy danych; aplikacja w pamięci i na plikach lokalnych.

<!-- docs:section next_actions -->
## Kolejne kroki

Wdrożenie procedury autoryzacji tokenowej.
