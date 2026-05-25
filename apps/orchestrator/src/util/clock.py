"""Timezone-aware ``utcnow`` helper.

``datetime.utcnow()`` is deprecated in Python 3.12+ and returns a naive
datetime which compares poorly with TZ-aware values. Use this helper for
all new code; existing call sites are being migrated incrementally.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utcnow_naive() -> datetime:
    """Return a naive UTC datetime, suitable for legacy SQLAlchemy ``DateTime`` columns.

    The DB models still use ``DateTime`` without ``timezone=True`` so values
    are stored naive. Until we widen the columns we strip ``tzinfo`` here
    to keep the wire format consistent.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
