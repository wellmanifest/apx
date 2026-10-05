# wellmanifest/apx

**Wellmanifest Standard for Autonomous Application Packs (APX)**

- **Standard ID**: `urn:wellmanifest:spec:apx:v1`
- **Manifest Schema**: `urn:willapx:manifest:v1` / `wellmanifest.apx/manifest/v1`
- **Governance**: `wellmanifest/new-project`

---

## 1. Dlaczego powstał standard APX?

W środowiskach wielookiennych (`willmux`), rozproszonych klastrach agentów (`willman`, `dockuri`) oraz platformach autonomicznych mikroaplikacji tworzenie osobnego repozytorium Git z kompletnym stosem CI dla każdego małego narzędzia utility powoduje niepotrzebny rozrost infrastruktury (*repository sprawl*).

Standard **Autonomous Application Pack (APX)** definiuje lekki, modułowy format paczki aplikacji (`apps/<app_id>`), który może działać w izolowanym procesie, oferując jednocześnie pełną integrację z pulpitami, czatem, rejestrem uprawnień i narzędziami orkiestracji.

---

## 2. Zasada komplementarności i zerowej duplikacji

Standard **`wellmanifest/apx` nie powiela istniejących standardów inżynierskich**. Zamiast tego pełni rolę **Standardu Kompozycji**, który precyzyjnie deleguje poszczególne obszary do dojrzałych standardów dziedzinowych `wellmanifest/*`:

| Obszar / Domena | Delegowany standard | Rola w paczce APX | Brak duplikacji |
| :--- | :--- | :--- | :--- |
| **Manifest & Sandbox** | [`wellmanifest/apx`](https://github.com/wellmanifest/apx) | `apx.yaml` (`urn:willapx:manifest:v1`) | Deklaruje metadane, punkt wejścia, port i granice uprawnień *least-privilege* (`resources`, `permissions`). |
| **Dokumentacja** | [`wellmanifest/docs`](https://github.com/wellmanifest/docs) | `doc/README.md` | Używa schematu `wellmanifest.docs/document/v1` z sekcjami: `purpose`, `scope`, `evidence`, `content`, `limitations`, `next_actions`. |
| **Kontrakt API & Podręcznik** | [`wellmanifest/usermanual`](https://github.com/wellmanifest/usermanual) | `doc/USER_MANUAL.md` lub `doc/usermanual/` | Ścisły podział CQRS na niemutujące zapytania (`GET`) i mutujące komendy (`POST`/`PUT`/`DELETE`) z audytem zero-drift. |
| **Logi i audyt zdarzeń** | [`wellmanifest/logs`](https://github.com/wellmanifest/logs) | `logger.py` | Emisja pojedynczych linii JSONL ze schematem `wellmanifest.logs/event/v1` oraz skatalogowanymi kodami błędów `APX-*`. |
| **Prawda konfiguracyjna** | [`wellmanifest/ssot`](https://github.com/wellmanifest/ssot) | `ssot.yaml` | `wellmanifest.ssot/v1` jako deklaratywne, niezmienne źródło prawdy dla portów, bindów sieciowych i kanonicznych tras. |
| **Dowód wykonania (Receipt)** | [`wellmanifest/wellman`](https://github.com/wellmanifest/wellman) | `willman.py` | Generowanie kryptograficznie podpisanych kwitów `ExecutionReceipt` (`wellmanifest.wellman/receipt/v1`) z hashem SHA-256. |
| **Tożsamość procesu & URI** | [`wellmanifest/uriprocess`](https://github.com/wellmanifest/uriprocess) | `server.py` | Adresowanie przez RFC 3986 Process URI (`process://<host>/apps/<app>/server.py`) i izolacja PID w `.apx/pids/`. |
| **Strumień konwersacyjny** | [`wellmanifest/nl-uri-dsl-llm`](https://github.com/wellmanifest/nl-uri-dsl-llm) | `DecisionCard v1` | Oddzielenie surowego CLI od czatu; interaktywne karty decyzji (`urn:dockuri:decision-card:v1`) do zatwierdzania akcji. |
| **Zasady governance** | [`wellmanifest/new-project`](https://github.com/wellmanifest/new-project) | `AGENTS.md` | Policy-as-code: modyfikacje wyłącznie przez tickety w worktree (`project/new-ticket.sh`), zakaz commitów bezpośrednio w `main`. |

---

## 3. Struktura paczki APX

Wzorcowa struktura katalogowa aplikacji (zobacz [`examples/minimal-app/`](examples/minimal-app/)):

```text
apps/<app-id>/
├── apx.yaml                 # Manifest APX (APX-MAN-001)
├── ssot.yaml                # Single Source of Truth (wellmanifest/ssot)
├── AGENTS.md                # Policy-as-Code governance (wellmanifest/new-project)
├── logger.py                # Rejestr zdarzeń JSONL (wellmanifest/logs)
├── willman.py               # Subaktor i kwity SHA-256 (wellmanifest/wellman)
├── server.py                # Punkt wejścia i kontrola /health (APX-HLT-001)
├── doc/
│   ├── README.md            # Dokumentacja architektoniczna (wellmanifest/docs)
│   └── usermanual/          # Specyfikacja CQRS (wellmanifest/usermanual)
│       ├── manifest.yaml
│       ├── queries/
│       └── commands/
└── web/                     # Interfejs PWA / ES Modules
    ├── index.html
    ├── app.js
    └── app.css
```

---

## 4. Sprawdzanie zgodności (Linter & Conformance Checker)

Pakiet zawiera oficjalny walidator zgodności `apx_check.py`:

```bash
# Weryfikacja katalogu aplikacji
python3 src/apx_check.py examples/minimal-app

# Weryfikacja z testem działającego endpointu /health
python3 src/apx_check.py examples/minimal-app --live-url http://127.0.0.1:8090

# Wyjście maszynowe JSON
python3 src/apx_check.py examples/minimal-app --json
```

---

## 5. Dokumentacja normatywna i schematy

* **Specyfikacja standardu**: [`spec/APX_STANDARD.md`](spec/APX_STANDARD.md)
* **Schemat JSON Schema**: [`schemas/apx-manifest.schema.json`](schemas/apx-manifest.schema.json)
* **Aplikacja referencyjna**: [`examples/minimal-app/`](examples/minimal-app/)

---

## 6. Uruchomienie testów

```bash
pytest -v
```
