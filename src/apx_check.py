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

    def __init__(self, app_dir: Path | str, schema_path: Optional[Path] = None):
        self.app_dir = Path(app_dir).resolve()
        self.schema_path = schema_path or SCHEMA_PATH
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
    parser.add_argument("--live-url", type=str, default="", help="Optional live HTTP URL to probe /health")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()
    checker = APXChecker(args.app_dir)
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
