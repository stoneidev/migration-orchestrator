"""Step 8: check that every spec operation is implemented by a Java endpoint.

Parses Spring ``@*Mapping`` annotations from generated Java files and matches
them against ``spec.operations``. This parser intentionally supports:
- class-level ``@RequestMapping`` prefixes
- method annotations with or without parentheses (``@GetMapping``)
- ``path=`` / ``value=`` route arguments
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


_METHOD_MAPPING_RE = re.compile(
    r"@(Get|Post|Put|Delete|Patch|Request)Mapping(?:\s*\(([^)]*)\))?",
    re.IGNORECASE | re.DOTALL,
)
_CLASS_REQUEST_MAPPING_RE = re.compile(
    r"@RequestMapping(?:\s*\(([^)]*)\))?\s*(?:public\s+)?(?:final\s+)?class\s+\w+",
    re.IGNORECASE | re.DOTALL,
)
_PATH_LITERAL_RE = re.compile(r'"([^"]+)"')
_NAMED_PATH_RE = re.compile(r"(?:path|value)\s*=\s*\"([^\"]+)\"", re.IGNORECASE)
_METHOD_RE = re.compile(r"method\s*=\s*(?:RequestMethod\.)?(GET|POST|PUT|DELETE|PATCH)", re.IGNORECASE)
_REQUEST_MAPPING_DEFAULT_METHOD = "GET"


@dataclass
class JavaEndpoint:
    http_method: str
    route: str
    file: str


@dataclass
class EquivalenceResult:
    success: bool
    covered: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    extra: list[dict] = field(default_factory=list)
    endpoints: list[dict] = field(default_factory=list)
    message: str = ""


def _resolve_java_path(file_ref: str, search_roots: list[Path]) -> Path | None:
    """``file_ref`` may be absolute, relative to a backend root, or just a name.

    Walk through ``search_roots`` until a matching file is found.
    """
    p = Path(file_ref)
    if p.is_absolute() and p.exists():
        return p
    for root in search_roots:
        candidate = root / file_ref
        if candidate.exists():
            return candidate
        # Fallback: search by basename if the path component cannot be resolved.
        matches = list(root.rglob(p.name))
        if matches:
            return matches[0]
    return None


def _extract_endpoints_from_text(text: str, file_label: str) -> list[JavaEndpoint]:
    class_prefix = ""
    class_spans: list[tuple[int, int]] = []
    for class_match in _CLASS_REQUEST_MAPPING_RE.finditer(text):
        args = class_match.group(1) or ""
        class_prefix = _extract_route_from_args(args)
        class_spans.append((class_match.start(), class_match.end()))

    endpoints: list[JavaEndpoint] = []
    for match in _METHOD_MAPPING_RE.finditer(text):
        # Skip class-level @RequestMapping used to declare the controller base path.
        if any(start <= match.start() < end for start, end in class_spans):
            continue

        annotation = match.group(1).capitalize()
        args = match.group(2) or ""
        route = _extract_route_from_args(args)

        if annotation == "Request":
            method_match = _METHOD_RE.search(args)
            http_method = method_match.group(1).upper() if method_match else _REQUEST_MAPPING_DEFAULT_METHOD
        else:
            http_method = annotation.upper()

        full_route = _join_route(class_prefix, route)
        endpoints.append(JavaEndpoint(http_method=http_method, route=full_route, file=file_label))
    return endpoints


def _extract_route_from_args(args: str) -> str:
    args = args.strip()
    if not args:
        return ""
    named = _NAMED_PATH_RE.search(args)
    if named:
        return named.group(1)
    first_literal = _PATH_LITERAL_RE.search(args)
    if first_literal:
        return first_literal.group(1)
    return ""


def _extract_endpoints(
    java_files: list[str],
    search_roots: list[Path],
) -> list[JavaEndpoint]:
    endpoints: list[JavaEndpoint] = []
    for file_ref in java_files:
        path = _resolve_java_path(file_ref, search_roots)
        if path is None:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        endpoints.extend(_extract_endpoints_from_text(text, file_label=str(path)))
    return endpoints


def _normalise_route(route: str) -> str:
    route = route.strip()
    if route and not route.startswith("/"):
        route = "/" + route
    # Strip trailing slash except when the route is just "/".
    if len(route) > 1 and route.endswith("/"):
        route = route.rstrip("/")
    return route


def _join_route(prefix: str, child: str) -> str:
    prefix_n = _normalise_route(prefix)
    child_n = _normalise_route(child)
    if prefix_n and child_n:
        return _normalise_route(prefix_n.rstrip("/") + "/" + child_n.lstrip("/"))
    return child_n or prefix_n


async def check_equivalence(
    spec: dict | None,
    java_files: list[str] | None = None,
    search_roots: list[Path] | None = None,
) -> EquivalenceResult:
    if spec is None:
        return EquivalenceResult(
            success=True,
            message="Spec not available — skipped",
        )

    operations = spec.get("operations", []) or []
    if not operations:
        return EquivalenceResult(
            success=True,
            message="No operations to check",
        )

    java_files = java_files or []
    if search_roots is None:
        search_roots = [Path.cwd()]

    endpoints = _extract_endpoints(java_files, search_roots)
    endpoint_routes_by_method: dict[str, set[str]] = {}
    for ep in endpoints:
        endpoint_routes_by_method.setdefault(ep.http_method.upper(), set()).add(_normalise_route(ep.route))

    covered: list[str] = []
    missing: list[str] = []
    matched_endpoints: set[tuple[str, str]] = set()

    for op in operations:
        op_id = (op.get("id") or "").strip()
        op_method = (op.get("http_method") or "GET").upper()
        op_route = _normalise_route(op.get("route", ""))

        matched = False

        if op_route:
            routes = endpoint_routes_by_method.get(op_method, set())
            if op_route in routes:
                matched = True
                matched_endpoints.add((op_method, op_route))

        if not matched and op_id:
            normalized_id = re.sub(r"[^a-z0-9]", "", op_id.lower())
            for file_ref in java_files:
                base = re.sub(r"[^a-z0-9]", "", Path(file_ref).stem.lower())
                if normalized_id and normalized_id in base:
                    matched = True
                    break

        if matched:
            covered.append(op_id or f"{op_method} {op_route}")
        else:
            missing.append(op_id or f"{op_method} {op_route}")

    extra: list[dict] = []
    for ep in endpoints:
        key = (ep.http_method.upper(), _normalise_route(ep.route))
        if key not in matched_endpoints:
            extra.append({"http_method": ep.http_method, "route": ep.route, "file": ep.file})

    return EquivalenceResult(
        success=len(missing) == 0,
        covered=covered,
        missing=missing,
        extra=extra,
        endpoints=[
            {"http_method": ep.http_method, "route": ep.route, "file": ep.file}
            for ep in endpoints
        ],
        message=(
            f"{len(covered)}/{len(operations)} operations covered"
            + (f", {len(missing)} missing" if missing else "")
            + (f", {len(extra)} extra endpoints" if extra else "")
        ),
    )
