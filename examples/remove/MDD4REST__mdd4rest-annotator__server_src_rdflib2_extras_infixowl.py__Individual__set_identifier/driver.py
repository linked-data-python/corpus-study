"""Validation driver for MDD4REST__mdd4rest-annotator__server_src_rdflib2_extras_infixowl.py__Individual__set_identifier.

`_set_identifier(self, i)` renames the node `self.__identifier` of
`self.graph` to `i`: it reads every statement where the old node is subject
or object, removes them, and adds them back with `i` in its place; it then
records a qname.  The method belongs to a class (infixowl.Individual) that is
not part of the region, so `self` is a stub with the three attributes the
region touches: `graph` (parsed from fixture.ttl, fresh for each side),
`__identifier`, `qname`.  The oracle is what the call leaves in that stub --
the harness compares an argument's state after the call, graph by
isomorphism -- and what it returns or raises.

Calls (fixture.ttl has the node ex:old with statements out and in, a
self-loop, a blank node object and a blank node subject, plus neighbours
that must stay where they are):

  * ex:old -> ex:new                a full rename, qname 'ex:new'
  * ex:old -> ex:old                nothing to do, only the qname is set
  * ex:nothing -> ex:ghost          a node with no statements: zero solutions
  * ex:old -> a fresh blank node    no qname for a blank node
  * the fixture's blank node -> ex:named    a blank node as the old identifier
  * ex:old -> http://example.org/dir/       compute_qname fails, caught
  * ex:old -> None                  `assert i` raised
"""
import types
from pathlib import Path

from rdflib import BNode, Namespace, URIRef

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
EX = Namespace("http://example.org/")


def _call(old, new):
    def build():
        g = fixture_graph(HERE / "fixture.ttl")
        identifier = old(g) if callable(old) else old
        target = new(g) if callable(new) else new
        stub = types.SimpleNamespace(**{"graph": g, "__identifier": identifier, "qname": None})
        return (stub, target), {}
    return build


def _anon(g):
    return g.value(EX.holder, EX.has)


VERDICT = run_pair(
    __file__,
    entry="_set_identifier",
    fixture="fixture.ttl",
    calls=[
        _call(EX.old, EX.new),
        _call(EX.old, EX.old),
        _call(EX.nothing, EX.ghost),
        _call(EX.old, lambda g: BNode()),
        _call(_anon, EX.named),
        _call(EX.old, URIRef("http://example.org/dir/")),
        _call(EX.old, None),
    ],
)
