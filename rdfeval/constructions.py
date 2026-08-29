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
