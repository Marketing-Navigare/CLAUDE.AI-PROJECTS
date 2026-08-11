#!/usr/bin/env python3
"""Gera workshop-estetica-avancada.html: a mesma landing page em arquivo unico,
com CSS, JS e imagens embutidos. Rode apos alterar index.html, styles.css,
main.js ou as fotografias em assets/img/."""

import base64
import mimetypes
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "index.html"
OUT = ROOT / "workshop-estetica-avancada.html"

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/avif", ".avif")

html = SRC.read_text(encoding="utf-8")
css = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")

html, n_css = re.subn(
    r'<link rel="stylesheet" href="assets/css/styles\.css">',
    lambda _: "<style>\n" + css + "\n</style>",
    html,
)
html, n_js = re.subn(
    r'<script src="assets/js/main\.js"></script>',
    lambda _: "<script>\n" + js + "\n</script>",
    html,
)

if n_css != 1 or n_js != 1:
    raise SystemExit(
        f"esperava 1 link de CSS e 1 de JS em index.html; encontrei {n_css} e {n_js}"
    )


def to_data_uri(rel_path: str) -> str | None:
    """Converte um asset local em data URI. Devolve None se o arquivo nao existir."""
    caminho = ROOT / rel_path
    if not caminho.is_file():
        return None
    mime = mimetypes.guess_type(caminho.name)[0] or "application/octet-stream"
    dados = base64.b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{dados}"


# Embute as imagens referenciadas em src="assets/..." e no fallback do onerror.
ausentes: list[str] = []
inline = 0


def substituir(m: re.Match) -> str:
    global inline
    prefixo, rel, sufixo = m.group(1), m.group(2), m.group(3)
    uri = to_data_uri(rel)
    if uri is None:
        ausentes.append(rel)
        return m.group(0)
    inline += 1
    return f"{prefixo}{uri}{sufixo}"


html = re.sub(r"""(src=")(assets/img/[^"]+)(")""", substituir, html)
html = re.sub(r"""(\.src=')(assets/img/[^']+)(')""", substituir, html)

OUT.write_text(html, encoding="utf-8")
print(f"{OUT.name} gerado ({len(html) / 1024:.1f} KB) — {inline} imagem(ns) embutida(s)")

for rel in sorted(set(ausentes)):
    print(f"  aviso: {rel} nao encontrado; a referencia foi mantida como caminho relativo")
