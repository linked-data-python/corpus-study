"""Inline the island reference into INSTRUCTIONS.md, from ldpy itself.

    python scripts/sync_language_reference.py [--check]

A translator agent used to be told to read nine pages of `../ldpy/docs/`
(~8500 words) before writing a line.  That is the cold start we pay on every
batch, and most of it is re-read of the same island table.

So the table is INLINED here instead — generated from
``ldpy.lsp.islanddoc``, which is itself pinned against the documentation by
``ldpy/tests/test_islanddoc.py`` (every kind described, every anchor alive).
One source, no drift, and an agent that starts with the reference already in
front of it.

``--check`` exits non-zero when the block is stale; a test calls it, so the
file cannot silently fall behind a language change.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

INSTRUCTIONS = Path(__file__).resolve().parent.parent / "INSTRUCTIONS.md"
BEGIN = "<!-- BEGIN island-reference (generated: sync_language_reference.py) -->"
END = "<!-- END island-reference -->"

# Kinds a translator never writes deliberately: `for-bindings-close` is the
# colon of a `for @bindings` header, mapped on its own because the header is
# rewritten in two pieces.  Listing it would be noise.
SKIP = {"for-bindings-close"}

# The order a translator meets them, not the alphabetical order.
ORDER = [
    ("Déclarations", ["prefix", "base", "import", "graph-decl",
                      "bindings-decl", "for-bindings"]),
    ("Termes", ["iri", "pname", "literal", "var", "firi", "fnode", "bnode"]),
    ("Graphes et graphe courant", ["graph", "addto", "removefrom"]),
    ("Lecture", ["match", "sparql"]),
    ("Évaluation différée", ["enode", "eiri"]),
]


def _cell(s: str) -> str:
    """A string safe inside a markdown table cell."""
    return s.replace("|", "\\|")


def render() -> str:
    from ldpy.lsp.islanddoc import ISLANDS
    out = [BEGIN, ""]
    for title, kinds in ORDER:
        out.append("**%s**" % title)
        out.append("")
        out.append("| forme | ce que c'est |")
        out.append("|---|---|")
        for kind in kinds:
            doc = ISLANDS[kind]
            sig = doc.signature.split(") ", 1)[1]
            # a bare `|` would close the table cell
            out.append("| `%s` | %s |" % (_cell(sig),
                                          _cell(doc.summary.replace("\n", " "))))
        out.append("")
    covered = {k for _, ks in ORDER for k in ks} | SKIP
    missing = sorted(set(ISLANDS) - covered)
    if missing:                                    # pragma: no cover
        raise SystemExit("island kinds absent from ORDER: %s" % missing)
    out.append("*(Engendré depuis `ldpy/lsp/islanddoc.py` — la table que le "
               "survol de l'éditeur affiche, en anglais comme tout le code. "
               "`ldpy/tests/test_islanddoc.py` garantit qu'elle décrit "
               "**toutes** les sortes d'îlot et que chacun de ses liens tombe "
               "sur une ancre vivante de la documentation. Ne l'éditez pas à "
               "la main : `python scripts/sync_language_reference.py`.)*")
    out.append("")
    out.append(END)
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the block is stale, write nothing")
    args = ap.parse_args()
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        raise SystemExit("markers not found in %s" % INSTRUCTIONS)
    head, rest = text.split(BEGIN, 1)
    _old, tail = rest.split(END, 1)
    new = head + render() + tail
    if new == text:
        print("island reference: up to date")
        return 0
    if args.check:
        print("island reference: STALE — run "
              "`python scripts/sync_language_reference.py`", file=sys.stderr)
        return 1
    INSTRUCTIONS.write_text(new, encoding="utf-8")
    print("island reference: updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
