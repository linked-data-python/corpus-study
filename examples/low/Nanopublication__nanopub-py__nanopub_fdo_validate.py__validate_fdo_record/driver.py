"""Validation driver for validate_fdo_record.

The region's only RDF behaviour is (a) building sh:resultMessage and (b)
reading it out of the SHACL report graph, so the fixtures take the
`profile_np is not None` branch — the one that needs neither the network nor
the handle registry.  `context._pyshacl_validate` returns a fixed report
graph (see context.py); both representations consume the very same object.
"""
from rdflib import Graph, Namespace, RDF

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")

SHAPES = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .
ex:FdoShape a sh:NodeShape ;
    sh:targetClass ex:Fdo ;
    sh:property [ sh:path ex:label ; sh:minCount 1 ] .
"""

DATA = """
@prefix ex: <http://example.org/> .
ex:fdo1 a ex:Fdo ; ex:hasProfile ex:profile1 .
"""


class _Record:
    """Duck-typed stand-in for nanopub.fdo.fdo_record.FdoRecord."""

    def __init__(self, data):
        self._data = data

    def get_graph(self):
        return Graph().parse(data=self._data, format="turtle")

    def get_profile(self):
        return EX.profile1

    def __eq__(self, other):  # the harness compares arguments after the call
        return isinstance(other, _Record) and self._data == other._data


class _ProfileNanopub:
    """Duck-typed stand-in for nanopub.fdo.fdo_nanopub.FdoNanopub."""

    def __init__(self, shapes):
        self.assertion = Graph().parse(data=shapes, format="turtle")

    def __eq__(self, other):
        from rdfeval.harness import normalise
        return (isinstance(other, _ProfileNanopub)
                and normalise(self.assertion) == normalise(other.assertion))


def with_profile():
    """Shape graph supplied directly: the report is read for sh:resultMessage."""
    return ((_Record(DATA), _ProfileNanopub(SHAPES)), {})


def no_shape_graph():
    """profile_np whose assertion is None -> the early-return branch."""
    np_ = _ProfileNanopub(SHAPES)
    np_.assertion = None
    return ((_Record(DATA), np_), {})


VERDICT = run_pair(__file__, entry="validate_fdo_record",
                   calls=[with_profile, no_shape_graph])
