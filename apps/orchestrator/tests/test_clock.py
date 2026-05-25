from datetime import datetime, timezone

from src.util.clock import utcnow, utcnow_naive


def test_utcnow_is_tz_aware():
    now = utcnow()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.utcoffset().total_seconds() == 0


def test_utcnow_naive_is_naive_but_close_to_utc():
    aware = datetime.now(timezone.utc)
    naive = utcnow_naive()
    assert naive.tzinfo is None
    # Within a small window (1s) of aware UTC.
    delta = abs((aware.replace(tzinfo=None) - naive).total_seconds())
    assert delta < 1.0
