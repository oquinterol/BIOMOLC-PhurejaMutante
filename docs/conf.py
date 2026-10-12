"""Sphinx configuration shared by local, CI and Read the Docs builds."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
project = "BIOMOLC-PhurejaMutante"
author = "BIOMOLC / Semillero de Agrigenómica"
copyright = "2022–2026, BIOMOLC"
release = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
version = release.split("-")[0]

extensions = ["myst_parser"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
language = "es"
exclude_patterns = ["_build", "requirements.txt", "requirements.in", ".DS_Store"]
nitpicky = True
myst_heading_anchors = 4

html_theme = "sphinx_rtd_theme"
html_title = f"{project} {release}"
html_logo = "biomolc.png"
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
    "sticky_navigation": True,
    "logo_only": False,
}
html_context = {
    "display_github": True,
    "github_user": "oquinterol",
    "github_repo": project,
    "github_version": "main",
    "conf_py_path": "/docs/",
}
