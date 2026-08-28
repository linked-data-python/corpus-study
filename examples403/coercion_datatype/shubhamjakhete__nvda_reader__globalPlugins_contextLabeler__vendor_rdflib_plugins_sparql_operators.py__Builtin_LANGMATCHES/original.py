# Extracted from shubhamjakhete/nvda_reader@8b5fb51e42 : globalPlugins/contextLabeler/_vendor/rdflib/plugins/sparql/operators.py
# region: Builtin_LANGMATCHES (lines 422-434, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql.parserutils import CompValue, Expr
from rdflib.term import (
    BNode,
    IdentifiedNode,
    Identifier,
    Literal,
    Node,
    URIRef,
    Variable,
)

def Builtin_LANGMATCHES(e: Expr, ctx) -> Literal:
    """
    http://www.w3.org/TR/sparql11-query/#func-langMatches


    """
    langTag = string(e.arg1)
    langRange = string(e.arg2)

    if str(langTag) == "":
        return Literal(False)  # nothing matches empty!

    return Literal(_lang_range_check(langRange, langTag))
