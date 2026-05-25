import pytest
from fastapi import HTTPException

from src.api.validators import (
    is_valid_page_id,
    safe_page_segment,
    validate_page_id,
)


@pytest.mark.parametrize(
    "page_id",
    [
        "shop.products",
        "ambassador.my_page",
        "bbs.alert_close",
        "shop_admin.cs_list",
        "single",
        "a.b.c.d.e",
        "page_with_underscore_123",
    ],
)
def test_valid_page_ids(page_id):
    assert is_valid_page_id(page_id) is True
    assert validate_page_id(page_id) == page_id


@pytest.mark.parametrize(
    "page_id",
    [
        "../etc/passwd",
        "shop/products",
        "Shop.Products",
        "shop products",
        ".leading.dot",
        "trailing.dot.",
        "double..dot",
        "shop.products!",
        "",
        "x" * 200,
    ],
)
def test_invalid_page_ids_rejected(page_id):
    assert is_valid_page_id(page_id) is False
    with pytest.raises(HTTPException) as exc:
        validate_page_id(page_id)
    assert exc.value.status_code == 400


def test_safe_page_segment_raises_value_error_for_path_traversal():
    with pytest.raises(ValueError):
        safe_page_segment("../../etc/passwd")


def test_safe_page_segment_returns_input_when_valid():
    assert safe_page_segment("shop.products") == "shop.products"


def test_validate_page_id_with_non_string_type():
    assert is_valid_page_id(None) is False
    assert is_valid_page_id(123) is False
