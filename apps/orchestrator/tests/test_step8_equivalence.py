import pytest
from pathlib import Path

from src.pipeline.steps.step8_equivalence import check_equivalence, _extract_endpoints_from_text


CONTROLLER_SOURCE = """
package com.silicon2.admin.shop;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/shop/products")
public class ProductController {

    @GetMapping("/list")
    public Object list() { return null; }

    @PostMapping("/create")
    public Object create() { return null; }

    @RequestMapping(value = "/legacy", method = RequestMethod.PUT)
    public Object legacy() { return null; }
}
"""


def test_extract_endpoints_from_text_parses_all_annotations():
    endpoints = _extract_endpoints_from_text(CONTROLLER_SOURCE, file_label="ProductController.java")
    methods = sorted((e.http_method, e.route) for e in endpoints)
    assert ("GET", "/list") in methods
    assert ("POST", "/create") in methods
    assert ("PUT", "/legacy") in methods
    # RequestMapping at class level too:
    assert any(e.route == "/api/v1/shop/products" for e in endpoints)


@pytest.mark.asyncio
async def test_check_equivalence_returns_success_when_all_ops_covered(tmp_path):
    java_file = tmp_path / "ProductController.java"
    java_file.write_text(CONTROLLER_SOURCE)

    spec = {
        "operations": [
            {"id": "list_products", "http_method": "GET", "route": "/list"},
            {"id": "create_product", "http_method": "POST", "route": "/create"},
        ],
    }

    result = await check_equivalence(
        spec=spec,
        java_files=[str(java_file)],
        search_roots=[tmp_path],
    )

    assert result.success is True
    assert set(result.covered) == {"list_products", "create_product"}
    assert result.missing == []


@pytest.mark.asyncio
async def test_check_equivalence_reports_missing(tmp_path):
    java_file = tmp_path / "ProductController.java"
    java_file.write_text(CONTROLLER_SOURCE)

    spec = {
        "operations": [
            {"id": "list_products", "http_method": "GET", "route": "/list"},
            {"id": "delete_product", "http_method": "DELETE", "route": "/delete"},
        ],
    }

    result = await check_equivalence(
        spec=spec,
        java_files=[str(java_file)],
        search_roots=[tmp_path],
    )

    assert result.success is False
    assert "delete_product" in result.missing


@pytest.mark.asyncio
async def test_check_equivalence_matches_by_filename_when_route_missing(tmp_path):
    java_file = tmp_path / "ListProductsController.java"
    java_file.write_text("public class ListProductsController {}")

    spec = {"operations": [{"id": "list_products"}]}

    result = await check_equivalence(
        spec=spec,
        java_files=[str(java_file)],
        search_roots=[tmp_path],
    )

    assert result.success is True
    assert "list_products" in result.covered


@pytest.mark.asyncio
async def test_check_equivalence_no_spec_passes():
    result = await check_equivalence(spec=None)
    assert result.success is True


@pytest.mark.asyncio
async def test_check_equivalence_no_operations_passes():
    result = await check_equivalence(spec={"operations": []})
    assert result.success is True
