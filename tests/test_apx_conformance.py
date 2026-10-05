import sys
from pathlib import Path
import tempfile
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.apx_check import APXChecker

ROOT = Path(__file__).resolve().parent.parent
MINIMAL_APP_DIR = ROOT / "examples" / "minimal-app"


def test_minimal_demo_app_conforms():
    """Verify that the bundled minimal-app passes all conformance checks."""
    assert MINIMAL_APP_DIR.exists(), f"Reference app not found at {MINIMAL_APP_DIR}"
    checker = APXChecker(MINIMAL_APP_DIR)
    res = checker.run()

    assert res["valid"] is True, f"Conformance audit failed: {res['errors']}"
    assert len(res["errors"]) == 0
    assert res["app"] == "minimal-demo"
    assert "docs" in res["delegations"]
    assert "usermanual" in res["delegations"]
    assert "logs" in res["delegations"]
    assert "ssot" in res["delegations"]


def test_missing_manifest_fails():
    """Verify that an empty directory without apx.yaml fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checker = APXChecker(tmpdir)
        res = checker.run()
        assert res["valid"] is False
        assert any("Missing required manifest" in err for err in res["errors"])


def test_invalid_schema_fails():
    """Verify that an unrecognized manifest schema fails APX-MAN-001."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        manifest = {
            "schema": "urn:invalid:schema:v1",
            "name": "bad-app",
            "title": "Bad App",
            "version": "1.0.0",
            "type": "web",
            "entrypoint": "server.py",
        }
        with open(tmp_path / "apx.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(manifest, f)
        (tmp_path / "server.py").write_text("print('hello')")

        checker = APXChecker(tmp_path)
        res = checker.run()
        assert res["valid"] is False
        assert any("Invalid schema" in err for err in res["errors"])


def test_missing_delegations_detected():
    """Verify that missing docs, usermanual, logs, ssot files fail APX-COMP-001."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        manifest = {
            "schema": "urn:willapx:manifest:v1",
            "name": "isolated-app",
            "title": "Isolated App",
            "version": "0.1.0",
            "type": "cli",
            "entrypoint": "cli.py",
        }
        with open(tmp_path / "apx.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(manifest, f)
        (tmp_path / "cli.py").write_text("print('cli')")

        checker = APXChecker(tmp_path)
        res = checker.run()

        assert res["valid"] is False
        # Must catch missing standard files
        errors_str = " ".join(res["errors"])
        assert "wellmanifest/docs" in errors_str
        assert "wellmanifest/usermanual" in errors_str
        assert "wellmanifest/logs" in errors_str
        assert "ssot.yaml" in errors_str


def test_faktury_app_audit_if_available():
    """Verify that willapx faktury app has valid apx.yaml and audits missing delegations accurately."""
    faktury_path = Path("/home/tom/github/paxlet-com/willapx/apps/faktury")
    if not faktury_path.exists():
        pytest.skip("willapx faktury app not found locally")

    checker = APXChecker(faktury_path)
    res = checker.run()
    assert res["app"] == "faktury"
    assert checker.manifest.get("schema") == "urn:willapx:manifest:v1"
    # Accurately pinpoints which complementary standards need scaffolding
    assert any("wellmanifest/docs" in err for err in res["errors"])
    assert any("logger.py" in err for err in res["errors"])
    assert any("ssot.yaml" in err for err in res["errors"])


def test_minimal_demo_container_profile_passes():
    """Verify that minimal-app passes container profile and dockuri checks."""
    checker = APXChecker(MINIMAL_APP_DIR, require_container=True)
    res = checker.run()
    assert res["valid"] is True, f"Container profile audit failed: {res['errors']}"
    assert len(res["errors"]) == 0


def test_missing_dockerfile_when_required_fails():
    """Verify that requiring container profile fails when Dockerfile is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        checker = APXChecker(tmp_path, require_container=True)
        res = checker.run()
        assert res["valid"] is False
        assert any("APX-DOCK-001" in err for err in res["errors"])
