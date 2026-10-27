"""The controlled vocabulary of language constructions.

The study credits or debits **each island separately**, so ``meta.json``'s
``constructions`` list is a headline measurement, not a comment.  Free text
does not survive that: the first wave produced ``nom préfixé`` and
``nom prefixe``, ``f<...>`` and ``f<…>``, ``suffixe d'appel (g)`` and
``call suffix (g)`` — four constructions where there are two.

:data:`CONSTRUCTIONS` is the canonical list, taken from the language
reference (``ldpy/docs/reference/language/index.md``).  :func:`normalise`
maps what a human or an agent actually writes onto it, and reports what it
could not place rather than dropping it: an unplaceable label is either a
typo to fix or a construction the vocabulary is missing, and both must be
visible.
"""

from __future__ import annotations

import re
import unicodedata

# Canonical names, grouped as the reference groups them.
CONSTRUCTIONS = (
    # declarations
    "@prefix", "@base", "from … import p:", "@graph", "@bindings",
    "for @bindings in",
    # graphs and the current graph
    "g{ }", "+{ }", "-{ }", "_:{ }",
    # reading
    "m{ }", "s{ }", ".first()", ".one()", ".count()", ".execute()",
    # deferred evaluation
    "e{ }", "e<…>", "f<…>", "f{ }",
    # terms
    "IRI", "prefixed name", "typed literal", "language literal",
    "plain literal", "variable", "interpolation {expr}",
    # context
    "call suffix (g)", "global/nonlocal modifier",
)

# What people write -> what it is.  Accents, spacing and the two languages of
# the project are folded away before lookup, so only real synonyms live here.
_ALIASES = {
    "nom prefixe": "prefixed name",
    "nom prefixe (pname)": "prefixed name",
    "pname": "prefixed name",
    "prefixed name (pname)": "prefixed name",
    "litteral type": "typed literal",
    "litteral typee": "typed literal",
    "litteral avec langue": "language literal",
    "litteral de langue": "language literal",
    "litteral simple": "plain literal",
    "litteral": "plain literal",
    "suffixe d'appel": "call suffix (g)",
    "suffixe d'appel (g)": "call suffix (g)",
    "call suffix": "call suffix (g)",
    "iri": "IRI",
    "ilot iri": "IRI",
    "variable (?v)": "variable",
    "import de prefixes": "from … import p:",
    "prefix import": "from … import p:",
    "interpolation": "interpolation {expr}",
    "{expr}": "interpolation {expr}",
    "global": "global/nonlocal modifier",
    "nonlocal": "global/nonlocal modifier",
    "f<...>": "f<…>",
    "e<...>": "e<…>",
    "first()": ".first()",
    "one()": ".one()",
    "count()": ".count()",
    "execute()": ".execute()",
}


def _fold(label: str) -> str:
    """Lower-case, unaccented, single-spaced, ellipsis normalised."""
    s = unicodedata.normalize("NFKD", label)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("…", "...").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


_CANON = {_fold(c): c for c in CONSTRUCTIONS}
_CANON.update({_fold(k): v for k, v in _ALIASES.items()})


def normalise(labels) -> tuple[list[str], list[str]]:
    """(canonical names, labels that could not be placed).

    Order is preserved and duplicates collapse, so a pair that names the same
    construction twice counts once.
    """
    seen: list[str] = []
    unknown: list[str] = []
    for label in labels or ():
        canon = _CANON.get(_fold(str(label)))
        if canon is None:
            if label not in unknown:
                unknown.append(label)
            continue
        if canon not in seen:
            seen.append(canon)
    return seen, unknown


# The constructions the transpiler's island spans identify without doubt.
# The others (`variable`, `interpolation {expr}`, the literals, `.first()`,
# `call suffix (g)`…) live inside an island's text and are not checked here.
_SPAN_KINDS = {
    "island:prefix": "@prefix", "island:base": "@base",
    "island:import": "from … import p:", "island:graph-decl": "@graph",
    "island:bindings-decl": "@bindings", "island:for-bindings": "for @bindings in",
    "island:graph": "g{ }", "island:addto": "+{ }",
    "island:removefrom": "-{ }", "island:match": "m{ }", "island:sparql": "s{ }",
    "island:fnode": "f{ }", "island:firi": "f<…>", "island:iri": "IRI",
}
CHECKED = frozenset(_SPAN_KINDS.values())


# An IRI or an f-IRI written INSIDE another island has no span of its own,
# so those two are also looked for in the text, outside the declarations.
_IRI_TEXT = re.compile(r"(?<![\w.])<[A-Za-z][\w+.-]*:[^>\s]*>")
_FIRI_TEXT = re.compile(r"(?<![\w.])f<")
_DECLARED_IRI = re.compile(r"(@prefix\s+[\w-]*:|@base)\s*<[^>]*>")


def detected(ldpy_source: str) -> set[str]:
    """The span-identifiable constructions a translation actually uses."""
    from .ldpy_metrics import measure_ldpy_source
    kinds = measure_ldpy_source(ldpy_source).island_kinds
    used = {_SPAN_KINDS[k] for k in kinds if k in _SPAN_KINDS}
    # drop comments and the plain IRI a declaration binds, nothing else
    body = "\n".join(line for line in ldpy_source.splitlines()
                     if not line.lstrip().startswith("#"))
    body = _DECLARED_IRI.sub("", body)
    if _IRI_TEXT.search(body.replace("f<", "f\x00")):
        used.add("IRI")
    if _FIRI_TEXT.search(body):
        used.add("f<…>")
    return used


def mismatch(declared, ldpy_source: str) -> tuple[list[str], list[str]]:
    """(declared but not used, used but not declared), checkable names only.

    A declared construction the code does not use is credited to the
    notation for nothing; a used one left undeclared is a construction the
    study fails to count.  Both bias the per-construction tables.
    """
    named, _ = normalise(declared)
    used = detected(ldpy_source)
    claimed = {c for c in named if c in CHECKED}
    return sorted(claimed - used), sorted(used - claimed)
