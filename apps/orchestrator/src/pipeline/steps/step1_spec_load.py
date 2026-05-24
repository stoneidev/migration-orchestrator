import json
from pathlib import Path


REQUIRED_SECTIONS = ["meta", "operations", "business_rules", "data_models", "test_scenarios"]


class SpecNotFoundError(Exception):
    pass


class SpecParseError(Exception):
    pass


class SpecValidationError(Exception):
    pass


def load_spec(spec_id: str, specs_dir: Path) -> dict:
    file_path = specs_dir / f"{spec_id}.aispec.json"

    if not file_path.exists():
        raise SpecNotFoundError(f"Spec not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        raise SpecParseError(f"Invalid JSON in {file_path}: {e}")

    for section in REQUIRED_SECTIONS:
        if section not in spec:
            raise SpecValidationError(f"Missing required section '{section}' in {spec_id}")

    if "id" not in spec.get("meta", {}):
        raise SpecValidationError(f"Missing 'meta.id' in {spec_id}")

    return spec
