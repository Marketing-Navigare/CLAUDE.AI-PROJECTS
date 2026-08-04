#!/usr/bin/env python3
"""Gera workshop-estetica-avancada.html: a mesma landing page em arquivo unico,
com CSS e JS embutidos. Rode apos alterar index.html, styles.css ou main.js."""

import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "index.html"
OUT = ROOT / "workshop-estetica-avancada.html"

html = SRC.read_text(encoding="utf-8")
css = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")

html, n_css = re.subn(
    r'<link rel="stylesheet" href="assets/css/styles\.css">',
    "<style>\n" + css + "\n</style>",
    html,
)
html, n_js = re.subn(
    r'<script src="assets/js/main\.js"></script>',
    "<script>\n" + js + "\n</script>",
    html,
)

if n_css != 1 or n_js != 1:
    raise SystemExit(
        f"esperava 1 link de CSS e 1 de JS em index.html; encontrei {n_css} e {n_js}"
    )

OUT.write_text(html, encoding="utf-8")
print(f"{OUT.name} gerado ({len(html) / 1024:.1f} KB)")
