"""Centralised logging configuration.

The orchestrator previously mixed ``print`` calls, raw ``logging.info``
with no handlers, and ad-hoc ``event_bus.emit("log", ...)`` lines. This
module wires a single ``StreamHandler`` once at startup so every module
that does ``logging.getLogger(__name__)`` gets consistent output, and
keeps the level adjustable via the ``ORCH_LOG_LEVEL`` env var.
"""

from __future__ import annotations

import logging
import os
import sys


_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_DATEFMT = "%H:%M:%S"


def configure_logging(level: str | None = None) -> None:
    """Idempotent root logger setup.

    Safe to call from tests; second invocations only adjust the level
    instead of stacking handlers.
    """
    root = logging.getLogger()
    resolved = (level or os.environ.get("ORCH_LOG_LEVEL") or "INFO").upper()
    root.setLevel(resolved)

    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT, _DEFAULT_DATEFMT))
        root.addHandler(handler)

    # Always (re)apply third-party logger caps, even on subsequent calls,
    # so tests can assert the levels deterministically regardless of
    # invocation order.
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
