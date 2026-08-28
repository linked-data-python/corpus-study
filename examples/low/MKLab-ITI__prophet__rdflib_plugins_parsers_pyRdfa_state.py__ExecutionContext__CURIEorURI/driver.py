"""Validation driver for ExecutionContext._CURIEorURI.

The region is a method: the fixtures below supply a minimal ``self`` that
provides exactly the attributes the body touches (base, rdfa_version,
options.add_warning, node.nodeName, term_or_curie.CURIE_to_URI, _URI).
The stub is defined here, so both representations receive a *fresh but
identical* one, and its ``__eq__`` compares the observable side effect
(the warnings recorded during the call).

Fixtures cover every branch: empty value, ill-formed safe CURIE,
unresolvable safe CURIE, resolvable CURIE, CURIE resolving to a relative
reference (the ``URIRef(self.base + ...)`` path), plain URI fallback and
the RDFa 1.0 branch.
"""
from rdflib import BNode, URIRef

from rdfeval.harness import run_pair

BASE = "http://example.org/doc/"
CURIES = {
    "foaf:name": URIRef("http://xmlns.com/foaf/0.1/name"),
    "ex:rel": URIRef("rel/target"),          # relative -> re-based by the region
    "ex:blank": BNode("b0"),
}


class _Options:
    def __init__(self):
        self.warnings = []

    def add_warning(self, txt, warning_type=None, context=None, node=None,
                    buggy_value=None):
        self.warnings.append((txt, warning_type, node))


class _Node:
    nodeName = "span"


class _State:
    """Stand-in for pyRdfa's ExecutionContext (the region's ``self``)."""

    def __init__(self, rdfa_version="1.1"):
        self.base = BASE
        self.rdfa_version = rdfa_version
        self.options = _Options()
        self.node = _Node()
        self.term_or_curie = self

    def CURIE_to_URI(self, val):
        return CURIES.get(val)

    def _URI(self, val):
        return URIRef(self.base + val) if "://" not in val else URIRef(val)

    def __eq__(self, other):
        return (isinstance(other, _State)
                and self.base == other.base
                and self.rdfa_version == other.rdfa_version
                and self.options.warnings == other.options.warnings)

    def __repr__(self):
        return "_State(%s, warnings=%r)" % (self.rdfa_version,
                                            self.options.warnings)


def case(val, version="1.1"):
    return lambda: ((_State(version), val), {})


VERDICT = run_pair(
    __file__,
    entry="_CURIEorURI",
    calls=[
        case(""),                     # -> URIRef(self.base)
        case("[foaf:name"),           # ill-formed safe CURIE -> warning, None
        case("[foaf:name]"),          # safe CURIE, resolvable
        case("[zz:unknown]"),         # safe CURIE, unresolvable -> warning, None
        case("foaf:name"),            # plain CURIE
        case("ex:rel"),               # CURIE -> relative ref -> re-based
        case("ex:blank"),             # CURIE -> BNode, left alone
        case("http://example.com/x"), # not a CURIE -> _URI fallback
        case("rel/x"),                # not a CURIE -> _URI fallback
        case("[foaf:name]", "1.0"),   # RDFa 1.0, safe CURIE
        case("foaf:name", "1.0"),     # RDFa 1.0, unsafe -> _URI
    ],
)
