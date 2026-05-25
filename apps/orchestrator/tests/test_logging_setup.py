import logging

from src.logging_setup import configure_logging


def test_configure_logging_idempotent():
    configure_logging("DEBUG")
    handlers_before = len(logging.getLogger().handlers)
    configure_logging("DEBUG")
    handlers_after = len(logging.getLogger().handlers)
    assert handlers_after == handlers_before


def test_configure_logging_respects_level_arg():
    configure_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING
    configure_logging("INFO")
    assert logging.getLogger().level == logging.INFO


def test_configure_logging_silences_botocore():
    configure_logging("DEBUG")
    assert logging.getLogger("botocore").level == logging.WARNING
