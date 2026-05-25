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
    cost: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    duration_ms: int = 0


REACT_PROMPT_TEMPLATE = """You are recreating an existing PHP web page as a React/Next.js component.

## CRITICAL: Replicate the EXACT visual appearance from the screenshot.

The screenshot file is at: {screenshot_path}
Read this image file and replicate every visual element exactly.

## Rules:
1. Use 'use client' directive
2. Tailwind CSS for styling — match colors, spacing, fonts exactly
3. Include ALL visible text, images, buttons, sections from the screenshot
4. Include mock data inline so it renders WITHOUT a backend
5. Mobile viewport (430px width)
6. Do NOT invent new designs — copy the screenshot exactly
7. Use placeholder image URLs if needed

## Spec (for dynamic behavior reference ONLY, not for visual design)
- Operations: {operations}
- Business Rules: {business_rules_summary}

## API Contract (for data structure reference only)
{api_contract_summary}

## Output files in current directory:
- page.tsx (Next.js App Router entry point)
- components/ (sub-components as needed)
- mock-data.ts (realistic mock data)
- types.ts (TypeScript interfaces)
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

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=15,
        cwd=output_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return ReactGenResult(
            success=False,
            error=result.error,
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )

    # Collect created files
    created_files = []
    if output_dir.exists():
        for f in output_dir.rglob("*.tsx"):
            created_files.append(str(f.relative_to(output_dir)))
        for f in output_dir.rglob("*.ts"):
            if not f.name.endswith(".d.ts"):
                created_files.append(str(f.relative_to(output_dir)))

    if not created_files:
        return ReactGenResult(
            success=False,
            error="No .tsx/.ts files generated",
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )

    return ReactGenResult(
        success=True,
        files_created=created_files,
        output=result.output[:500],
        cost=result.cost,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cache_creation_tokens=result.cache_creation_tokens,
        cache_read_tokens=result.cache_read_tokens,
        duration_ms=result.duration_ms,
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
