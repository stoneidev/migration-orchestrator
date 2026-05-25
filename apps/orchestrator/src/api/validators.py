"""Input validators for API entry points.

`page_id` is concatenated into filesystem paths by pipeline steps (e.g.
``page_id.replace(".", "/")``) so unvalidated input would allow path traversal.
All API routes that accept a ``page_id`` MUST pass it through
:func:`validate_page_id` before forwarding it to the pipeline.
"""

from __future__ import annotations

import re

from fastapi import HTTPException

PAGE_ID_PATTERN = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")
MAX_PAGE_ID_LENGTH = 128


def is_valid_page_id(page_id: str) -> bool:
    if not isinstance(page_id, str):
        return False
    if not page_id or len(page_id) > MAX_PAGE_ID_LENGTH:
        return False
    return bool(PAGE_ID_PATTERN.match(page_id))


def validate_page_id(page_id: str) -> str:
    """Return ``page_id`` if it matches the allowed pattern, else raise 400."""
    if not is_valid_page_id(page_id):
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION-001",
                    "message": (
                        f"Invalid page_id '{page_id}'. Allowed pattern: "
                        f"{PAGE_ID_PATTERN.pattern}"
                    ),
                },
            },
        )
    return page_id


def safe_page_segment(page_id: str) -> str:
    """Defensive last-mile check before joining ``page_id`` into a filesystem path.

    Raises :class:`ValueError` rather than ``HTTPException`` so it can be used
    outside the request/response cycle (e.g. inside background tasks).
    """
    if not is_valid_page_id(page_id):
        raise ValueError(f"Unsafe page_id for path use: {page_id!r}")
    return page_id
