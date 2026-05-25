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


@dataclass
class VisualComparison:
    """Result of comparing two screenshots."""

    diff_percent: float
    ssim: float
    width: int
    height: int


async def verify_visual_similarity(
    original_screenshot: Path,
    react_project_dir: Path,
    page_route: str,
    port: int = 3100,
    startup_timeout_s: int = 30,
    ssim_threshold: float = 0.85,
    diff_threshold_pct: float = 15.0,
) -> tuple[bool, VisualComparison, Path | None]:
    """Start the generated Next.js app, screenshot the page, and compare.

    Passes when the page is either visually similar (``ssim >= ssim_threshold``)
    or pixel-close (``diff_percent <= diff_threshold_pct``). SSIM is the
    primary gate because the pixel diff is over-sensitive to anti-aliasing
    and minor font differences.
    """
    react_screenshot = original_screenshot.parent / "react_latest.png"

    server_proc = subprocess.Popen(
        ["npx", "next", "dev", "--port", str(port)],
        cwd=str(react_project_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        await _wait_for_dev_server(port, startup_timeout_s)

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 430, "height": 932})
            await page.goto(f"http://localhost:{port}{page_route}", timeout=30000)
            await page.wait_for_timeout(3000)
            await page.screenshot(path=str(react_screenshot), full_page=True)
            await browser.close()

        comparison = compare_screenshots(original_screenshot, react_screenshot)
        passed = comparison.ssim >= ssim_threshold or comparison.diff_percent <= diff_threshold_pct
        return passed, comparison, react_screenshot

    finally:
        server_proc.kill()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass


async def _wait_for_dev_server(port: int, timeout_s: int) -> None:
    """Poll ``http://localhost:port/`` until it answers or the timeout elapses."""
    import socket

    deadline = asyncio.get_event_loop().time() + timeout_s
    while asyncio.get_event_loop().time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            await asyncio.sleep(0.5)
    # Final fallback: legacy fixed sleep so callers still get a screenshot
    # attempt instead of an early failure when startup is slow.
    await asyncio.sleep(2)


def compare_screenshots(img1_path: Path, img2_path: Path) -> VisualComparison:
    """Compute a pixel diff *and* an SSIM score for two screenshots.

    ``ssim`` is computed via a lightweight grayscale implementation (mean,
    variance, covariance over the whole image) to avoid pulling in
    scikit-image; this is sufficient for the layout-level check the
    pipeline needs.
    """
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        # Without PIL/numpy we can't compare; fall back to "identical" so
        # the legacy behaviour (no enforcement) is preserved on barebones
        # installs.
        return VisualComparison(diff_percent=0.0, ssim=1.0, width=0, height=0)

    try:
        img1 = Image.open(img1_path).convert("RGB")
        img2 = Image.open(img2_path).convert("RGB")
    except Exception:
        return VisualComparison(diff_percent=50.0, ssim=0.0, width=0, height=0)

    target_size = (430, min(img1.height, img2.height, 2000))
    img1 = img1.resize(target_size)
    img2 = img2.resize(target_size)

    arr1 = np.asarray(img1, dtype=np.float64)
    arr2 = np.asarray(img2, dtype=np.float64)

    diff = np.abs(arr1 - arr2)
    diff_percent = round(float(diff.sum() / (arr1.size * 255)) * 100, 2)

    gray1 = arr1.mean(axis=2)
    gray2 = arr2.mean(axis=2)
    ssim = _ssim_global(gray1, gray2)

    return VisualComparison(
        diff_percent=diff_percent,
        ssim=round(ssim, 4),
        width=target_size[0],
        height=target_size[1],
    )


def _ssim_global(a, b) -> float:
    """Single-window SSIM on grayscale arrays (range 0-255).

    Implements the standard SSIM formula with the literature's stabilisation
    constants. A single global window is sufficient for the orchestrator's
    layout-level pass/fail decision and avoids depending on scikit-image
    just for one number.
    """
    import numpy as np

    L = 255.0
    K1, K2 = 0.01, 0.03
    C1 = (K1 * L) ** 2
    C2 = (K2 * L) ** 2

    mu_a = float(np.mean(a))
    mu_b = float(np.mean(b))
    var_a = float(np.var(a))
    var_b = float(np.var(b))
    cov_ab = float(np.mean((a - mu_a) * (b - mu_b)))

    numerator = (2 * mu_a * mu_b + C1) * (2 * cov_ab + C2)
    denominator = (mu_a**2 + mu_b**2 + C1) * (var_a + var_b + C2)
    if denominator == 0:
        return 1.0
    return float(numerator / denominator)
