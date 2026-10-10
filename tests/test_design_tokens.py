"""One design system, three surfaces — this test keeps them consistent.

The Streamlit app (`ui.TOKENS`), its native theme (`.streamlit/config.toml`), and
the static landing page (`landing/styles.css`) all carry the same values. Without
this guard the three quietly drift apart, which is exactly how a UI ends up
looking like several different products.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ui  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".streamlit" / "config.toml"
LANDING_CSS = ROOT / "landing" / "styles.css"
LANDING_HTML = ROOT / "landing" / "index.html"

# Streamlit theme keys that must carry a token value, and the token they carry.
THEME_COLOUR_MAP = {
    "primaryColor": "brand",
    "backgroundColor": "surface",
    "secondaryBackgroundColor": "surface-sunken",
    "textColor": "ink",
    "linkColor": "brand-strong",
    "borderColor": "border",
}


def _theme_table(text: str) -> dict[str, str]:
    """Return the flat ``[theme]`` table as strings.

    Uses ``tomllib`` where available (Python 3.11+) and falls back to a minimal
    reader for the flat key/value table this project keeps in that file.
    """
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python 3.10
        section = re.search(r"^\[theme\]$(.*?)(^\[|\Z)", text, re.S | re.M)
        assert section, "config.toml has no [theme] table"
        return {
            key: value.strip().strip('"')
            for key, value in re.findall(
                r'^([A-Za-z0-9_]+)\s*=\s*(".*?")\s*$', section.group(1), re.M
            )
        }

    data = tomllib.loads(text)
    assert "theme" in data, "config.toml has no [theme] table"
    return {
        key: str(value) for key, value in data["theme"].items() if isinstance(value, str)
    }


def _css_root_vars(text: str) -> dict[str, str]:
    """Return the ``--akx-*`` custom properties declared in the first ``:root``."""
    root = re.search(r":root\s*\{(.*?)\}", text, re.S)
    assert root, "landing stylesheet has no :root block"
    return {
        name: value.strip()
        for name, value in re.findall(r"--akx-([a-z0-9-]+)\s*:\s*([^;]+);", root.group(1))
    }


def test_theme_colours_come_from_the_shared_tokens():
    theme = _theme_table(CONFIG.read_text(encoding="utf-8"))
    for key, token in THEME_COLOUR_MAP.items():
        assert theme[key] == ui.TOKENS[token], f"{key} must equal ui.TOKENS[{token!r}]"


def test_landing_page_declares_every_shared_token():
    variables = _css_root_vars(LANDING_CSS.read_text(encoding="utf-8"))
    missing = sorted(set(ui.TOKENS) - set(variables))
    assert not missing, f"landing/styles.css is missing tokens: {missing}"
    for name, value in ui.TOKENS.items():
        assert variables[name] == value, f"--akx-{name} differs from ui.TOKENS"


def test_landing_page_uses_the_shared_stylesheet_only():
    """The landing page must not grow a second, competing style source."""
    html = LANDING_HTML.read_text(encoding="utf-8")
    assert html.count("<style") == 0, "landing page should link styles.css, not inline CSS"
    assert 'href="styles.css"' in html


def test_both_surfaces_cover_devanagari():
    """Nepali must render on both surfaces without a webfont dependency."""
    theme = _theme_table(CONFIG.read_text(encoding="utf-8"))
    assert "Noto Sans Devanagari" in theme["font"]
    assert "Noto Sans Devanagari" in ui.stylesheet()
    assert "Noto Sans Devanagari" in LANDING_CSS.read_text(encoding="utf-8")
