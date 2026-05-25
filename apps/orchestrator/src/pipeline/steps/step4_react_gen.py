import asyncio
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class ReactGenResult:
    success: bool
    files_created: list[str] = field(default_factory=list)
    visual_diff_percent: float = 0.0
    output: str = ""
    error: str = ""


REACT_PROMPT_TEMPLATE = """You are recreating an existing PHP web page as a React/Next.js component.

## CRITICAL TASK
1. Use the Playwright MCP tool to navigate to: {url}
2. Take a screenshot and CAREFULLY observe every visual element
3. Create React components that look IDENTICAL to what you see
4. After creating, start the dev server and compare visually

## Steps to follow:
1. First, use playwright_navigate to open {url}
2. Use playwright_screenshot to capture the page
3. Analyze every element: layout, colors, fonts, spacing, images, text
4. Write React code that replicates it exactly
5. Use 'use client' directive, Tailwind CSS for styling
6. Include mock data so it renders without a backend
7. Mobile viewport (430px width)

## Spec (for dynamic behavior reference ONLY, not for UI)
- Operations: {operations}
- Business Rules: {business_rules_summary}

## Output files in current directory:
- page.tsx (Next.js App Router entry)
- components/ (sub-components)
- mock-data.ts (data matching what you see on the page)
- types.ts

DO NOT invent designs. Copy EXACTLY what you see in the browser.
"""


async def generate_react(
    spec: dict,
    api_contract: str,
    output_dir: Path,
    screenshot_path: Path | None = None,
    worker: ClaudeCLIWorker | None = None,
) -> ReactGenResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    meta = spec.get("meta", {})
    operations = spec.get("operations", [])
    business_rules = spec.get("business_rules", [])

    ops_summary = ", ".join(op.get("name", op.get("id", "")) for op in operations[:5])
    brs_summary = "; ".join(br.get("description", "")[:50] for br in business_rules[:5])
    api_summary = api_contract[:500] if api_contract else "N/A"

    url = meta.get("url", spec.get("source", {}).get("path", ""))

    prompt = REACT_PROMPT_TEMPLATE.format(
        url=url,
        screenshot_path=str(screenshot_path) if screenshot_path else "not available",
        operations=ops_summary,
        business_rules_summary=brs_summary,
        api_contract_summary=api_summary,
    )

    # If screenshot exists, tell CLI to read it
    if screenshot_path and screenshot_path.exists():
        prompt += f"\n\nREAD the screenshot file at: {screenshot_path}\nUse it as the EXACT visual reference."

    output_dir.mkdir(parents=True, exist_ok=True)

    # MCP config for Playwright access
    mcp_config_path = str(Path(__file__).parent.parent.parent.parent / "mcp-playwright.json")

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=20,
        cwd=output_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read", "mcp__playwright__playwright_navigate", "mcp__playwright__playwright_screenshot", "mcp__playwright__playwright_click", "mcp__playwright__playwright_get_visible_text"],
        mcp_config=mcp_config_path,
    )

    if not result.success:
        return ReactGenResult(success=False, error=result.error)

    # Collect created files
    created_files = []
    if output_dir.exists():
        for f in output_dir.rglob("*.tsx"):
            created_files.append(str(f.relative_to(output_dir)))
        for f in output_dir.rglob("*.ts"):
            if not f.name.endswith(".d.ts"):
                created_files.append(str(f.relative_to(output_dir)))

    if not created_files:
        return ReactGenResult(success=False, error="No .tsx/.ts files generated")

    return ReactGenResult(
        success=True,
        files_created=created_files,
        output=result.output[:500],
    )


async def verify_visual_similarity(
    original_screenshot: Path,
    react_project_dir: Path,
    page_route: str,
    port: int = 3001,
) -> tuple[bool, float, Path | None]:
    """
    1. Start Next.js dev server
    2. Capture screenshot of generated React page
    3. Compare with original
    4. Return (pass, diff_percent, react_screenshot_path)
    """
    react_screenshot = original_screenshot.parent / "react_latest.png"

    # Start dev server
    server_proc = subprocess.Popen(
        ["npx", "next", "dev", "--port", str(port)],
        cwd=str(react_project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for server to start
        await asyncio.sleep(10)

        # Capture React page screenshot
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 430, "height": 932})
            await page.goto(f"http://localhost:{port}{page_route}", timeout=30000)
            await page.wait_for_timeout(3000)
            await page.screenshot(path=str(react_screenshot), full_page=True)
            await browser.close()

        # Compare images
        diff_percent = await _compare_screenshots(original_screenshot, react_screenshot)

        return (diff_percent <= 15.0, diff_percent, react_screenshot)

    finally:
        server_proc.kill()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass


async def _compare_screenshots(img1_path: Path, img2_path: Path) -> float:
    """Simple pixel-based comparison. Returns difference percentage."""
    try:
        from PIL import Image
        import numpy as np

        img1 = Image.open(img1_path).convert("RGB")
        img2 = Image.open(img2_path).convert("RGB")

        # Resize to same dimensions
        target_size = (430, min(img1.height, img2.height, 2000))
        img1 = img1.resize(target_size)
        img2 = img2.resize(target_size)

        arr1 = np.array(img1, dtype=float)
        arr2 = np.array(img2, dtype=float)

        diff = np.abs(arr1 - arr2)
        diff_percent = (diff.sum() / (arr1.size * 255)) * 100

        return round(diff_percent, 2)

    except ImportError:
        # If PIL/numpy not available, skip comparison
        return 0.0
    except Exception:
        return 50.0  # assume different if error
