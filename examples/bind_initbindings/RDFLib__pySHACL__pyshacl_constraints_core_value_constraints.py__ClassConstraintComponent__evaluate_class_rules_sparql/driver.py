"""Validation driver for the pySHACL ClassConstraintComponent region.

The region is a method: `self` is a stub with the two things it touches,
`shape.logger.debug` (prints, so stdout shows it) and `make_v_result`
(returns a tuple recording its arguments, so the reports are visible).

Calls (each re-parses the fixture):
  * values at depth 2 (rex), depth 0 (fido), a sibling branch (tweety), a
    super-class instance (rock), a node only linked by another predicate
    (ghost) and a Literal -- two conformant, four reported, the Literal
    taking the debug branch;
  * a class with no instance at all: every value is reported;
  * an empty f_v_dict: nothing reported, (False, []).
"""
from pathlib import Path
from types import SimpleNamespace

from rdflib import Literal, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"


class _Logger:
    def debug(self, msg):
        print("DEBUG", msg)


class _Component:
    def __init__(self):
        self.shape = SimpleNamespace(logger=_Logger())

    def make_v_result(self, target_graph, f, value_node=None):
        return ("report", f, value_node)


def _values():
    return [URIRef(EX + n) for n in ("rex", "fido", "tweety", "rock", "ghost")] \
        + [Literal("rex")]


def call(f_v_dict, cls):
    def _make():
        return (_Component(), fixture_graph(FIXTURE), f_v_dict(), URIRef(EX + cls)), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='_evaluate_class_rules_sparql',
    calls=[
        call(lambda: {URIRef(EX + "c1"): _values()}, "Animal"),
        call(lambda: {URIRef(EX + "c1"): _values()[:2], URIRef(EX + "c2"): _values()[2:4]}, "Mammal"),
        call(lambda: {URIRef(EX + "c1"): _values()}, "Unused"),
        call(lambda: {}, "Animal"),
    ],
)
