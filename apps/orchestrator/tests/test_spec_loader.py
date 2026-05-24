from pathlib import Path

from src.pipeline.steps.step1_spec_load import load_spec

SPECS_DIR = Path("/Users/stoni/Projects/silicon2/harness/specs")


def test_load_spec_bbs_alert_close():
    spec = load_spec("bbs.alert_close", specs_dir=SPECS_DIR)

    assert spec["meta"]["id"] == "bbs.alert_close"
    assert spec["meta"]["status"] == "complete"
    assert "operations" in spec
    assert len(spec["operations"]) == 1
    assert "business_rules" in spec
    assert len(spec["business_rules"]) == 6
    assert "test_scenarios" in spec
    assert len(spec["test_scenarios"]) >= 10


def test_load_spec_returns_all_sections():
    spec = load_spec("bbs.alert_close", specs_dir=SPECS_DIR)

    required_sections = ["meta", "operations", "business_rules", "data_models", "test_scenarios"]
    for section in required_sections:
        assert section in spec, f"Missing section: {section}"


import pytest
from src.pipeline.steps.step1_spec_load import SpecNotFoundError, SpecParseError, SpecValidationError
import tempfile
import json


def test_spec_not_found():
    with pytest.raises(SpecNotFoundError):
        load_spec("nonexistent.page", specs_dir=SPECS_DIR)


def test_invalid_json():
    with tempfile.TemporaryDirectory() as tmp:
        bad_file = Path(tmp) / "bad.spec.aispec.json"
        bad_file.write_text("{ invalid json", encoding="utf-8")
        with pytest.raises(SpecParseError):
            load_spec("bad.spec", specs_dir=Path(tmp))


def test_missing_required_section():
    with tempfile.TemporaryDirectory() as tmp:
        incomplete = {"meta": {"id": "test"}, "operations": []}
        spec_file = Path(tmp) / "test.incomplete.aispec.json"
        spec_file.write_text(json.dumps(incomplete), encoding="utf-8")
        with pytest.raises(SpecValidationError, match="business_rules"):
            load_spec("test.incomplete", specs_dir=Path(tmp))
