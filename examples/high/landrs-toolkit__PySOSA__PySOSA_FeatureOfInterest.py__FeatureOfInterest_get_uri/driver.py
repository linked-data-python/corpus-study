"""Validation driver for FeatureOfInterest.get_uri.

The region is a getter followed by three UNREACHABLE ``obsgraph.add(...)``
statements (they sit after the ``return``; the source's own ``sosa`` name is
not even imported in that file, so they would raise NameError if they ever
ran).  No fixture can therefore exercise the RDF part: what the driver
establishes is that both representations compile, that the reachable
statement returns the same term, and that neither side touches ``obsgraph``.

That the two spellings of the dead code build the same three triples was
checked separately, on scratch copies with the ``return`` moved to the end
(see meta.json).
"""
from rdflib import BNode, Graph, Literal, URIRef

from rdfeval.harness import normalise, run_pair


class Foi:
    """Stand-in for the FeatureOfInterest whose URI is asked for."""

    def __init__(self, identifier, label, comment):
        self.feature_of_interest_id = identifier
        self.label = Literal(label)
        self.comment = Literal(comment)

    def __eq__(self, other):
        return isinstance(other, Foi) and normalise(vars(self)) == normalise(vars(other))

    def __repr__(self):
        return "Foi(%r)" % (vars(self),)


def named():
    return ((Foi(URIRef("http://example.org/site/grenoble"),
                 "Air temperature sensor site",
                 "A field station in Grenoble"),), {})


def anonymous():
    return ((Foi(BNode(), "Air temperature sensor site",
                 "A field station in Grenoble"),), {})


VERDICT = run_pair(__file__, entry="get_uri", calls=[named, anonymous])
