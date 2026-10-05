"""Willman subactor and ExecutionReceipt interface for minimal-demo."""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Optional


def create_execution_receipt(
    action: str,
    status: str = "completed",
    payload: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Emit signed ExecutionReceipt according to wellmanifest/wellman standard."""
    now = time.time()
    body = {
        "schema": "wellmanifest.wellman/receipt/v1",
        "app": "minimal-demo",
        "action": action,
        "status": status,
        "timestamp": now,
        "payload": payload or {},
    }
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    body["receipt_sha256"] = digest
    body["urn"] = f"urn:willapx:minimal-demo:receipt:{digest[:16]}"
    return body
