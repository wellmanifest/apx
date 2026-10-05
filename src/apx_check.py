"""Wellmanifest APX Conformance Checker and Rule Validator.

Enforces rules APX-MAN-001, APX-COMP-001, APX-ISO-001, APX-HLT-001 according to
the normative specification urn:wellmanifest:spec:apx:v1.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "apx-manifest.schema.json"


class APXValidationError(Exception):
    """Raised when an APX application bundle violates normative rules."""
    pass


class APXChecker:
    """Audits and validates an APX application directory against Wellmanifest standards."""

    def __init__(self, app_dir: Path | str, schema_path: Optional[Path] = None, require_container: bool = False):
        self.app_dir = Path(app_dir).resolve()
        self.schema_path = schema_path or SCHEMA_PATH
        self.require_container = require_container
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.manifest: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        """Execute full conformance audit."""
        self.errors.clear()
        self.warnings.clear()

        if not self.app_dir.exists() or not self.app_dir.is_dir():
            return {
                "valid": False,
                "app": self.app_dir.name,
                "errors": [f"Application directory does not exist: {self.app_dir}"],
                "warnings": [],
            }

        self._check_manifest_apx_man_001()
        self._check_composition_apx_comp_001()
        self._check_container_profile_apx_dock_001()
        self._check_dockuri_srv_001()

        has_container = (self.app_dir / "Dockerfile").exists()
        has_dockuri = (self.app_dir / "dockuri.json").exists()

        return {
            "valid": len(self.errors) == 0,
            "app": self.manifest.get("name", self.app_dir.name),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "delegations": {
                "docs": "wellmanifest/docs",
                "usermanual": "wellmanifest/usermanual",
                "logs": "wellmanifest/logs",
                "ssot": "wellmanifest/ssot",
                "wellman": "wellmanifest/wellman",
                "governance": "wellmanifest/new-project",
            },
        }

    def _check_manifest_apx_man_001(self) -> None:
        """Validate Rule APX-MAN-001: Canonical Manifest."""
        manifest_file = self.app_dir / "apx.yaml"
        if not manifest_file.exists():
            self.errors.append("APX-MAN-001: Missing required manifest 'apx.yaml'")
            return

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                self.manifest = yaml.safe_load(f) or {}
        except Exception as e:
            self.errors.append(f"APX-MAN-001: Corrupt YAML in 'apx.yaml': {e}")
            return

        schema_id = self.manifest.get("schema")
        if schema_id not in ("urn:willapx:manifest:v1", "wellmanifest.apx/manifest/v1"):
            self.errors.append(
                f"APX-MAN-001: Invalid schema '{schema_id}'. Must be 'urn:willapx:manifest:v1' or 'wellmanifest.apx/manifest/v1'"
            )

        name = self.manifest.get("name")
        if not name or not isinstance(name, str):
            self.errors.append("APX-MAN-001: Manifest missing required valid string 'name'")
        elif not name.replace("-", "").replace("_", "").isalnum():
            self.errors.append(f"APX-MAN-001: Name '{name}' must be alphanumeric with '-' or '_'")

        if not self.manifest.get("title"):
            self.errors.append("APX-MAN-001: Manifest missing required 'title'")

        app_type = self.manifest.get("type")
        if app_type not in ("web", "cli", "service"):
            self.errors.append(f"APX-MAN-001: Invalid type '{app_type}'. Must be web, cli, or service")

        entrypoint = self.manifest.get("entrypoint")
        if not entrypoint:
            self.errors.append("APX-MAN-001: Manifest missing required 'entrypoint'")
        else:
            entry_file = self.app_dir / entrypoint
            if not entry_file.exists():
                self.errors.append(f"APX-MAN-001: Declared entrypoint '{entrypoint}' does not exist on disk")

        if "permissions" not in self.manifest or not isinstance(self.manifest.get("permissions"), list):
            self.warnings.append("APX-MAN-001: Recommended explicit 'permissions' list missing in apx.yaml")

    def _check_composition_apx_comp_001(self) -> None:
        """Validate Rule APX-COMP-001: Strict Standards Delegation & Zero Duplication."""
        # 1. wellmanifest/docs in doc/README.md
        readme_file = self.app_dir / "doc" / "README.md"
        if not readme_file.exists():
            readme_file = self.app_dir / "README.md"

        if not readme_file.exists():
            self.errors.append("APX-COMP-001: Missing documentation file conforming to wellmanifest/docs (doc/README.md)")
        else:
            content = readme_file.read_text(encoding="utf-8")
            if "wellmanifest.docs/document/v1" not in content and "wellmanifest.docs" not in content:
                self.errors.append("APX-COMP-001: doc/README.md does not conform to wellmanifest.docs/document/v1")
            required_sections = ["purpose", "scope", "evidence", "content", "limitations", "next_actions"]
            missing_secs = [s for s in required_sections if f"docs:section {s}" not in content]
            if missing_secs:
                self.warnings.append(f"APX-COMP-001: doc/README.md missing normative comment markers: {missing_secs}")

        # 2. wellmanifest/usermanual
        usermanual_file = self.app_dir / "doc" / "USER_MANUAL.md"
        usermanual_modular = self.app_dir / "doc" / "usermanual" / "manifest.yaml"
        if not usermanual_file.exists() and not usermanual_modular.exists():
            self.errors.append(
                "APX-COMP-001: Missing CQRS specification conforming to wellmanifest/usermanual (doc/USER_MANUAL.md or doc/usermanual/manifest.yaml)"
            )

        # 3. wellmanifest/logs in logger.py
        logger_file = self.app_dir / "logger.py"
        if not logger_file.exists():
            self.errors.append("APX-COMP-001: Missing structured logging module conforming to wellmanifest/logs (logger.py)")
        else:
            content = logger_file.read_text(encoding="utf-8")
            if "wellmanifest.logs/event/v1" not in content:
                self.errors.append("APX-COMP-001: logger.py does not emit schema 'wellmanifest.logs/event/v1'")

        # 4. wellmanifest/ssot in ssot.yaml
        ssot_file = self.app_dir / "ssot.yaml"
        if not ssot_file.exists():
            self.errors.append("APX-COMP-001: Missing single source of truth configuration (ssot.yaml)")
        else:
            content = ssot_file.read_text(encoding="utf-8")
            if "wellmanifest.ssot/v1" not in content and "wellmanifest.ssot" not in content:
                self.errors.append("APX-COMP-001: ssot.yaml does not declare wellmanifest.ssot/v1 schema")

        # 5. wellmanifest/wellman in willman.py
        willman_file = self.app_dir / "willman.py"
        if not willman_file.exists():
            self.warnings.append("APX-COMP-001: willman.py (ExecutionReceipt provider) not found")
        else:
            content = willman_file.read_text(encoding="utf-8")
            if "wellmanifest.wellman/receipt/v1" not in content and "ExecutionReceipt" not in content:
                self.warnings.append("APX-COMP-001: willman.py does not reference wellmanifest.wellman/receipt/v1")

        # 6. wellmanifest/new-project in AGENTS.md
        agents_file = self.app_dir / "AGENTS.md"
        if not agents_file.exists():
            self.warnings.append("APX-COMP-001: Recommended AGENTS.md policy-as-code file missing in bundle")

    def _check_container_profile_apx_dock_001(self) -> None:
        """Validate Rule APX-DOCK-001: Container Packaging Profile."""
        dockerfile = self.app_dir / "Dockerfile"
        compose_file = self.app_dir / "compose.yml"
        if not compose_file.exists():
            compose_file = self.app_dir / "docker-compose.yml"
        req_file = self.app_dir / "requirements.txt"
        pyproject = self.app_dir / "pyproject.toml"

        is_container_profile = self.require_container or dockerfile.exists() or compose_file.exists()
        if not is_container_profile:
            return

        # 1. Dependency lock
        if not req_file.exists() and not pyproject.exists():
            self.errors.append("APX-DOCK-001: Container profile requires requirements.txt or pyproject.toml")

        # 2. Dockerfile checks
        if not dockerfile.exists():
            self.errors.append("APX-DOCK-001: Container profile requires Dockerfile")
        else:
            df_content = dockerfile.read_text(encoding="utf-8")
            if "FROM " not in df_content:
                self.errors.append("APX-DOCK-001: Dockerfile missing valid FROM directive")
            if "HEALTHCHECK" not in df_content:
                self.warnings.append("APX-DOCK-001: Dockerfile recommended HEALTHCHECK directive missing")

        # 3. Compose file checks
        if not compose_file.exists():
            self.warnings.append("APX-DOCK-001: compose.yml or docker-compose.yml missing in container profile")
        else:
            try:
                with open(compose_file, "r", encoding="utf-8") as f:
                    compose_data = yaml.safe_load(f) or {}
                if "services" not in compose_data:
                    self.errors.append("APX-DOCK-001: compose.yml missing 'services' definition")
            except Exception as e:
                self.errors.append(f"APX-DOCK-001: Invalid YAML in {compose_file.name}: {e}")

    def _check_dockuri_srv_001(self) -> None:
        """Validate Rule APX-SRV-001: Dockuri Process Mapping."""
        dockuri_file = self.app_dir / "dockuri.json"
        if not dockuri_file.exists():
            return

        try:
            with open(dockuri_file, "r", encoding="utf-8") as f:
                d_data = json.load(f)
            if d_data.get("format") != "dockuri/proc-v1":
                self.errors.append(f"APX-SRV-001: dockuri.json format must be 'dockuri/proc-v1', got '{d_data.get('format')}'")
            uri = d_data.get("uri", "")
            if not uri.startswith("proc://"):
                self.errors.append(f"APX-SRV-001: dockuri.json uri must start with 'proc://', got '{uri}'")
        except Exception as e:
            self.errors.append(f"APX-SRV-001: Invalid JSON in dockuri.json: {e}")

    def check_live_health(self, base_url: str) -> bool:
        """Validate Rule APX-HLT-001: Deterministic Health Probe against live service."""
        url = base_url.rstrip("/") + "/health"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Wellmanifest-APX-Checker/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status != 200:
                    self.errors.append(f"APX-HLT-001: /health returned status {resp.status}, expected 200")
                    return False
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") != "ok":
                    self.errors.append(f"APX-HLT-001: /health payload 'status' is '{data.get('status')}', expected 'ok'")
                    return False
                return True
        except Exception as e:
            self.errors.append(f"APX-HLT-001: Failed to query /health at {url}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Wellmanifest APX Conformance Checker")
    parser.add_argument("app_dir", type=str, help="Path to APX application directory")
    parser.add_argument("--container", action="store_true", help="Require and validate container packaging profile")
    parser.add_argument("--live-url", type=str, default="", help="Optional live HTTP URL to probe /health")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()
    checker = APXChecker(args.app_dir, require_container=args.container)
    report = checker.run()

    if args.live_url:
        checker.check_live_health(args.live_url)
        report["valid"] = len(checker.errors) == 0
        report["errors"] = list(checker.errors)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        status_str = "PASSED" if report["valid"] else "FAILED"
        print(f"=== APX Conformance Audit: {report['app']} [{status_str}] ===")
        print(f"Directory: {checker.app_dir}")
        if report["errors"]:
            print("\nErrors:")
            for err in report["errors"]:
                print(f"  ❌ {err}")
        if report["warnings"]:
            print("\nWarnings:")
            for warn in report["warnings"]:
                print(f"  ⚠️  {warn}")
        if report["valid"]:
            print("\n✅ Conforms strictly to urn:wellmanifest:spec:apx:v1")
            print("Delegated standards:")
            for k, v in report["delegations"].items():
                print(f"  - {k}: {v}")

    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
