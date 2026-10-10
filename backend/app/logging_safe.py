"""Filtro de logs: impede que imagens em base64, data URLs e credenciais apareçam."""
from __future__ import annotations

import logging
import re

_PATTERNS = [
    (re.compile(r"data:image/[a-zA-Z+.-]+;base64,[A-Za-z0-9+/=]+"), "data:image/[omitido]"),
    (re.compile(r"[A-Za-z0-9+/]{160,}={0,2}"), "[base64 omitido]"),
    (re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), "sk-[omitido]"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{8,}"), "Bearer [omitido]"),
    (re.compile(r"(?i)(api[_-]?key|password|senha|token)(\s*[=:]\s*)\S+"), r"\1\2[omitido]"),
]


def redact(text: str) -> str:
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - nunca derrubar o log
            return True
        clean = redact(message)
        if clean != message:
            record.msg, record.args = clean, ()
        return True


def install() -> None:
    flt = RedactingFilter()
    for name in ("", "uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "vesteia"):
        logger = logging.getLogger(name)
        if not any(isinstance(f, RedactingFilter) for f in logger.filters):
            logger.addFilter(flt)
        for handler in logger.handlers:
            if not any(isinstance(f, RedactingFilter) for f in handler.filters):
                handler.addFilter(flt)
