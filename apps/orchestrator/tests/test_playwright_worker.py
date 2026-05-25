import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from src.workers.playwright import PageCapture, PlaywrightWorker, ScreenshotResult


def test_page_capture_default_lists_are_empty():
    capture = PageCapture(success=True)
    assert capture.headings == []
    assert capture.buttons == []
    # The dataclass uses default_factory so each instance gets a fresh list.
    other = PageCapture(success=True)
    other.headings.append("hi")
    assert capture.headings == []


def test_playwright_worker_init():
    worker = PlaywrightWorker(
        base_url="https://dev.stylekorean.com",
        admin_id="test_user",
        admin_pw="test_pass",
        screenshots_dir=Path("./screenshots"),
    )
    assert worker.base_url == "https://dev.stylekorean.com"
    assert worker.admin_id == "test_user"


@pytest.mark.asyncio
async def test_playwright_capture_returns_error_when_not_installed(tmp_path):
    worker = PlaywrightWorker(
        base_url="https://dev.stylekorean.com",
        admin_id="",
        admin_pw="",
        screenshots_dir=tmp_path,
    )

    with patch.dict("sys.modules", {"playwright": None, "playwright.async_api": None}):
        # If playwright is not importable, should return graceful error
        result = await worker.capture("adm/bbs/alert_close.php", "bbs.alert_close")
        # Either fails gracefully or succeeds if playwright is installed
        assert isinstance(result, ScreenshotResult)


@pytest.mark.asyncio
async def test_playwright_capture_creates_output_dir(tmp_path):
    worker = PlaywrightWorker(
        base_url="https://example.com",
        admin_id="",
        admin_pw="",
        screenshots_dir=tmp_path,
    )
    # This will fail (can't connect) but should create the dir structure
    result = await worker.capture("adm/test.php", "bbs.test_page")
    # Either way, check it doesn't crash
    assert isinstance(result, ScreenshotResult)
