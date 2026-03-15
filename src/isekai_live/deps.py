"""Dependency checks for Python and file prerequisites."""

from importlib.util import find_spec
from pathlib import Path


REQUIRED_MODULES = ("makelive",)


def ensure_dependencies() -> None:
    """Raise if a required Python dependency is unavailable."""
    missing = [module for module in REQUIRED_MODULES if find_spec(module) is None]
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(f"Missing required Python package(s): {names}")


def ensure_file_exists(path: Path, label: str) -> None:
    """Raise if the requested input file does not exist."""
    if not path.is_file():
        raise RuntimeError(f"{label} not found: {path}")
