import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path


log = logging.getLogger(__name__)


@dataclass
class ScreenshotResult:
    success: bool
    file_path: str = ""
    error: str = ""


@dataclass
class PageCapture:
    """Captured page used by the spec-gen flow.

    Includes the original screenshot plus enough DOM signal (headings,
    button labels, title) to seed the LLM prompt without a second
    network round-trip.
    """
    success: bool
    screenshot_path: str = ""
    url: str = ""
    title: str = ""
    headings: list[str] = field(default_factory=list)
    buttons: list[str] = field(default_factory=list)
    error: str = ""


class PlaywrightWorker:
    def __init__(self, base_url: str, admin_id: str, admin_pw: str, screenshots_dir: Path):
        self.base_url = base_url
        self.admin_id = admin_id
        self.admin_pw = admin_pw
        self.screenshots_dir = screenshots_dir
        self._browser = None
        self._context = None

    async def capture(self, page_path: str, page_id: str) -> ScreenshotResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return ScreenshotResult(success=False, error="playwright not installed. Run: pip install playwright && playwright install chromium")

        output_dir = self.screenshots_dir / page_id.replace(".", "_")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "original.png"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": 1440, "height": 900})
                page = await context.new_page()

                # Login
                await self._login(page)

                # Navigate to target page
                url = f"{self.base_url}/{page_path}"
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(1000)

                # Capture screenshot
                await page.screenshot(path=str(output_file), full_page=True)

                await browser.close()

            return ScreenshotResult(success=True, file_path=str(output_file))

        except Exception as e:
            return ScreenshotResult(success=False, error=str(e))

    async def _login(self, page) -> None:
        login_url = f"{self.base_url}/adm/login_check.php"

        # Navigate to admin login page
        await page.goto(f"{self.base_url}/adm/", wait_until="networkidle", timeout=15000)

        # Fill login form
        await page.fill('input[name="mb_id"]', self.admin_id)
        await page.fill('input[name="mb_password"]', self.admin_pw)

        # Submit
        await page.click('input[type="submit"], button[type="submit"]')
        await page.wait_for_load_state("networkidle", timeout=10000)

    async def capture_for_spec(
        self,
        target_url: str,
        page_id: str,
        *,
        login_url_path: str = "/manage-account/gologin.php",
        viewport: tuple[int, int] = (430, 932),
    ) -> PageCapture:
        """Capture a fully-rendered page plus its high-level structure.

        Used by the spec-gen flow. Combines the login + capture from the
        old inline implementation in ``routes/spec_gen`` with the structured
        DOM extraction the LLM prompt needs.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return PageCapture(success=False, error="playwright not installed")

        output_dir = self.screenshots_dir / page_id
        output_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = output_dir / "original.png"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": viewport[0], "height": viewport[1]})
                page = await context.new_page()

                await page.goto(f"{self.base_url}{login_url_path}", timeout=60000)
                await page.wait_for_timeout(2000)
                email = page.locator('input[name="mb_id"]:visible').first
                if await email.count() > 0:
                    await email.fill(self.admin_id)
                pw_field = page.locator('input[type="password"]:visible').first
                if await pw_field.count() > 0:
                    await pw_field.fill(self.admin_pw)
                submit = page.locator('input[type="submit"]:visible').first
                if await submit.count() > 0:
                    await submit.click()
                await page.wait_for_timeout(5000)

                await page.goto(target_url, timeout=60000)
                await page.wait_for_timeout(5000)

                await page.screenshot(path=str(screenshot_path), full_page=True)

                headings = await page.locator("h1,h2,h3,h4").all_text_contents()
                buttons = await page.locator("button, a[class*='btn']").all_text_contents()
                title = await page.title()
                final_url = page.url

                await browser.close()

            return PageCapture(
                success=True,
                screenshot_path=str(screenshot_path),
                url=final_url,
                title=title,
                headings=[h.strip() for h in headings if h.strip()][:10],
                buttons=[b.strip() for b in buttons if b.strip()][:10],
            )

        except Exception as e:
            log.exception("playwright capture_for_spec failed for %s", page_id)
            return PageCapture(success=False, error=str(e))

    async def capture_react(self, react_url: str, page_id: str) -> ScreenshotResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return ScreenshotResult(success=False, error="playwright not installed")

        output_dir = self.screenshots_dir / page_id.replace(".", "_")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "react_latest.png"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1440, "height": 900})
                await page.goto(react_url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(500)
                await page.screenshot(path=str(output_file), full_page=True)
                await browser.close()

            return ScreenshotResult(success=True, file_path=str(output_file))
        except Exception as e:
            return ScreenshotResult(success=False, error=str(e))
