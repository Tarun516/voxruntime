"""Architecture tests that keep the domain package independent of adapters."""

import ast
from pathlib import Path

DOMAIN_ROOT = Path(__file__).parents[2] / "src" / "voxruntime" / "domain"
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {"adapters", "apps", "fastapi", "livekit", "psycopg", "redis"}
)


def imported_roots(source_file: Path) -> set[str]:
    """Return top-level import names found in one Python source file.

    Args:
        source_file: Python file whose abstract syntax tree will be inspected.

    Returns:
        Unique top-level module names imported by the source file.

    Solution category:
        Static dependency analysis using a linear abstract-syntax-tree walk.

    Complexity:
        O(n) time and O(i) auxiliary space, where ``n`` is the number of syntax
        nodes and ``i`` is the number of distinct imported roots in the file.
        The function reads the complete source file into memory once.
    """
    # 1. Parse source text without importing or executing the module.
    tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=source_file)
    roots: set[str] = set()

    # 2. Collect the first name segment from both Python import forms.
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", maxsplit=1)[0])

    return roots


def test_domain_does_not_import_infrastructure() -> None:
    """Domain rules remain runnable without application or vendor packages."""
    python_files = sorted(DOMAIN_ROOT.rglob("*.py"))

    violations = {
        source_file.relative_to(DOMAIN_ROOT): imported_roots(source_file)
        & FORBIDDEN_IMPORT_ROOTS
        for source_file in python_files
    }

    assert not {path: roots for path, roots in violations.items() if roots}
