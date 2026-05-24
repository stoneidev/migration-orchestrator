import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScreenshotResult:
    success: bool
    file_path: str = ""
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
