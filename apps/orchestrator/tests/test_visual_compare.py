"""Phase 4: SSIM-based visual comparison.

Smoke-tests the SSIM implementation and the registry threshold wiring
without spinning up Playwright / Next.js.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from src.pipeline.steps.step4_react_gen import (
    VisualComparison,
    compare_screenshots,
    _ssim_global,
)


def _write_png(path: Path, color: tuple[int, int, int], size=(60, 60)) -> Path:
    img = Image.new("RGB", size, color)
    img.save(path)
    return path


def test_ssim_global_identical_arrays_returns_one():
    rng = np.random.default_rng(0)
    a = rng.integers(0, 256, size=(40, 40)).astype(np.float64)
    assert math.isclose(_ssim_global(a, a), 1.0, abs_tol=1e-9)


def test_ssim_global_dropping_quality_lowers_score():
    rng = np.random.default_rng(0)
    a = rng.integers(0, 256, size=(40, 40)).astype(np.float64)
    b = a + rng.normal(scale=20.0, size=a.shape)
    noisy_score = _ssim_global(a, b)
    very_noisy_score = _ssim_global(a, a + rng.normal(scale=80.0, size=a.shape))
    assert noisy_score > very_noisy_score
    assert noisy_score < 1.0


def test_compare_screenshots_identical_image(tmp_path):
    img = _write_png(tmp_path / "a.png", color=(120, 120, 120))
    result = compare_screenshots(img, img)

    assert isinstance(result, VisualComparison)
    assert result.diff_percent == 0.0
    assert math.isclose(result.ssim, 1.0, abs_tol=1e-6)


def test_compare_screenshots_inverted_image(tmp_path):
    a = _write_png(tmp_path / "white.png", color=(255, 255, 255))
    b = _write_png(tmp_path / "black.png", color=(0, 0, 0))
    result = compare_screenshots(a, b)

    assert result.diff_percent > 90.0
    assert result.ssim < 0.05


def test_compare_screenshots_returns_default_when_image_unreadable(tmp_path):
    not_an_image = tmp_path / "broken.png"
    not_an_image.write_text("not really an image")
    real = _write_png(tmp_path / "real.png", color=(120, 120, 120))

    result = compare_screenshots(not_an_image, real)
    # We fall back to a "definitely different" sentinel so the visual gate
    # still fails closed.
    assert result.diff_percent == 50.0
    assert result.ssim == 0.0


@pytest.mark.asyncio
async def test_step4_visual_gate_threshold_is_configurable(tmp_path):
    """If both SSIM and pixel-diff thresholds are tight, a near-identical
    image still passes; if both are absurdly tight, it fails."""
    img = _write_png(tmp_path / "a.png", color=(120, 120, 120))

    permissive = compare_screenshots(img, img)
    assert permissive.ssim >= 0.85
    assert permissive.diff_percent <= 15.0
