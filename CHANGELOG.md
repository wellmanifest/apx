# Changelog

All notable changes to `wellmanifest/apx` will be documented in this file.

## [0.1.0] - 2026-10-05

### Added
- Initial specification of Autonomous Application Pack (APX) standard (`urn:wellmanifest:spec:apx:v1`).
- JSON Schema for `apx.yaml` (`urn:willapx:manifest:v1` / `wellmanifest.apx/manifest/v1`).
- Standard conformance checker `src/apx_check.py` validating composition, isolation, and standard delegation.
- Comprehensive test suite in `tests/test_apx_conformance.py`.
- Minimal reference application in `examples/minimal-app/`.
- Full cross-linking and complementary integration with `wellmanifest/{docs,usermanual,logs,ssot,wellman,new-project,uriprocess}`.
