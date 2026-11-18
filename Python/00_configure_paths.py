"""Directories used by the Pan-human Azimuth label inventory."""

from pathlib import Path


def configure_paths(root):
    root = Path(root).resolve()
    paths = {
        "root": root,
        "python": root / "Python",
        "models": root / "models",
        "tables": root / "tables",
        "paper": root / "paper",
    }
    for key in ("models", "tables", "paper"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths
