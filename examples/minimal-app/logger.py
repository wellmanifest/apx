"""Structured logging conforming to wellmanifest/logs standard for minimal-demo."""
from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any, Optional

DIAGNOSTIC_CODES = {
    "APX-INIT-001": "Inicjalizacja aplikacji apx",
    "APX-START-001": "Uruchomienie serwera aplikacji",
    "APX-HEALTH-001": "Kontrola stanu zdrowia /health",
    "APX-ACTION-001": "Wykonanie akcji biznesowej",
    "APX-ERR-001": "Błąd wewnętrzny serwera",
}


class ApxLogger:
    def __init__(self, app_id: str = "minimal-demo"):
        self.app_id = app_id
        self._logger = logging.getLogger(app_id)
        if not self._logger.handlers:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(h)
            self._logger.setLevel(logging.INFO)

    def log(self, code: str, message: str, level: str = "INFO", extra: Optional[dict[str, Any]] = None):
        record = {
            "schema": "wellmanifest.logs/event/v1",
            "timestamp": time.time(),
            "app": self.app_id,
            "code": code,
            "level": level,
            "message": message,
            "description": DIAGNOSTIC_CODES.get(code, ""),
            **(extra or {}),
        }
        line = json.dumps(record, ensure_ascii=False)
        if level in ("ERROR", "CRITICAL"):
            self._logger.error(line)
        elif level == "WARNING":
            self._logger.warning(line)
        else:
            self._logger.info(line)


log = ApxLogger()
