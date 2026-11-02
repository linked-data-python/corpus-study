"""Validation driver for comp-rob2b__kindyngen__kindynsyn_synthesizer_graph_factories_dynamics.py__DynamicsEntitiesCoordinates_inertial_wrench.

`inertial_wrench(self, inertia, twist, wrench)` makes thirteen assertions
about a graph (`self.g`) and, if they all hold, adds four triples about a
fresh blank-free UUID IRI and returns it.  A failed assertion raises a bare
`AssertionError()` with no message, and raising is compared like a value, so
two runs that fail at different assertions would look alike.  The driver
therefore makes the region show WHICH reads it made:

  * `self` is a small object whose `g` is a `ReadLog` (a real rdflib Graph
    whose `triples()` records the (subject, predicate) of every pattern the
    region asks)
    and whose `reads` list is an attribute of `self`: it is part of the
    mutations the harness compares, argument by argument, after each call.
    `g.value`, the `g[s:p]` slice and the `m{ }` island all read through
    `triples()`, so the two sides must ask about the same (subject,
    predicate) pairs in the same order; the point where a failing run stops
    shows in the log.  (The object position is left out of the record: `o in
    g[s:p]` scans the objects of (s, p), the island's existence test asks
    (s, p, o) directly -- the same question, not the same call.)
  * `uuid.uuid4` is replaced, in the driver process before the sides fork
    from it, by a deterministic counter, so `uuid_ref()` gives the same IRI
    on both sides.

Calls (each on a fresh graph read from fixture.ttl, then edited):
  base            everything agrees: returns the IRI and adds four triples
  swap_*          the subject/predicate roles are passed in another order
  one case per assertion (asb_twist, asb_wrench, ref_twist, ref_wrench,
  body_twist, body_wrench, unit_1 .. unit_7): the fixture is edited so that
  exactly that assertion fails; the log stops there
  none_*          a property missing from BOTH sides of an equality: the
                  values are None == None, which holds
  two_values      the inertia has two as-seen-by values: the first one read
                  is what is compared
  wrong_ns        the three as-seen-by of the inertia and wrench are moved
                  to the geometry namespace: the reads must find nothing
  empty           an empty graph: first equality None == None holds, the
                  first unit assertion fails
"""
import itertools
import sys
import unittest.mock
import uuid
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = Namespace("http://example.org/")
GC = Namespace("https://comp-rob2b.github.io/metamodels/geometry/coordinates#")
GR = Namespace("https://comp-rob2b.github.io/metamodels/geometry/spatial-relations#")
RE = Namespace("https://comp-rob2b.github.io/metamodels/newtonian-rigid-body-dynamics/structural-entities#")
RC = Namespace("https://comp-rob2b.github.io/metamodels/newtonian-rigid-body-dynamics/coordinates#")
QS = Namespace("http://qudt.org/schema/qudt/")
QU = Namespace("http://qudt.org/vocab/unit/")

_counter = itertools.count(1)
uuid.uuid4 = lambda: uuid.UUID(int=next(_counter))


def _in_region(name="inertial_wrench"):
    """True while the region's function is on the stack: the harness itself
    reads the argument graph after the call, and that is not the region."""
    f = sys._getframe(2)
    while f is not None:
        if f.f_code.co_name == name:
            return True
        f = f.f_back
    return False


class ReadLog(Graph):
    """A Graph that records the patterns the REGION asks of `triples()` and
    the triples yielded, in a list owned by the caller."""

    def __init__(self, reads, *a, **kw):
        super().__init__(*a, **kw)
        self._reads = reads

    def triples(self, triple):
        if _in_region():
            # (subject, predicate) only: `o in g[s:p]` scans the objects of
            # (s, p) while the island's existence test asks (s, p, o)
            # directly -- same question, not the same call.
            self._reads.append(("ask", triple[0], triple[1]))
        yield from super().triples(triple)


class Self:
    """Stand-in for DynamicsEntitiesCoordinates: only `.g` is used."""

    def __init__(self, edit=None):
        self.reads = []
        self.g = ReadLog(self.reads)
        self.g.parse(source=str(FIXTURE), format="turtle")
        if edit:
            edit(self.g)
        self.reads.clear()


ARGS = (EX.inertia, EX.twist, EX.wrench)


def call(edit=None, args=ARGS):
    def c():
        return ((Self(edit),) + tuple(args), {})
    return c


def removing(*triples):
    def edit(g):
        for t in triples:
            g.remove(t)
    return edit


def adding(*triples):
    def edit(g):
        for t in triples:
            g.add(t)
    return edit


def both(*edits):
    def edit(g):
        for e in edits:
            e(g)
    return edit


def change(s, p, old, new):
    return both(removing((s, p, old)), adding((s, p, new)))


CALLS = [
    call(),
    call(args=(EX.inertia2, EX.twist2, EX.wrench2)),            # the other, also consistent, triple
    call(args=(EX.inertia, EX.twist2, EX.wrench)),               # twist of another frame: assertion 1
    call(args=(EX.inertia, EX.twist, EX.wrench2)),               # wrench of another frame: assertion 2
    # one assertion at a time
    call(change(EX.twist, GC["as-seen-by"], EX.frame1, EX.frame9)),            # 1
    call(change(EX.wrench, RC["as-seen-by"], EX.frame1, EX.frame9)),           # 2
    call(change(EX.velocityRel, GR["reference-point"], EX.point1, EX.point9)),  # 3
    call(change(EX.wrenchRel, RE["reference-point"], EX.point1, EX.point9)),    # 4
    call(change(EX.velocityRel, GR["of"], EX.body1, EX.body9)),                 # 5
    call(change(EX.wrenchRel, RE["acts-on"], EX.body1, EX.body9)),              # 6
    call(removing((EX.inertia, QS["unit"], QU["KiloGM"]))),                     # 7
    call(removing((EX.inertia, QS["unit"], QU["M-KiloGM"]))),                   # 8
    call(removing((EX.inertia, QS["unit"], QU["KiloGM-M2"]))),                  # 9
    call(removing((EX.twist, QS["unit"], QU["RAD-PER-SEC"]))),                  # 10
    call(removing((EX.twist, QS["unit"], QU["M-PER-SEC"]))),                    # 11
    call(removing((EX.wrench, QS["unit"], QU["N-M"]))),                         # 12
    call(removing((EX.wrench, QS["unit"], QU["N"]))),                           # 13
    # a unit that is only a quantityKind of the same subject does not count
    call(both(removing((EX.wrench, QS["unit"], QU["N-M"])),
              adding((EX.wrench, QS["quantityKind"], QU["N-M"])))),
    # a unit the inertia does not have but another subject does
    call(both(removing((EX.inertia, QS["unit"], QU["KiloGM"])),
              adding((EX.twist, QS["unit"], QU["KiloGM"])))),
    # None == None holds when a property is missing from both sides
    call(removing((EX.twist, GC["as-seen-by"], EX.frame1),
                  (EX.inertia, RC["as-seen-by"], EX.frame1))),            # 1 holds (None == None), 2 fails
    call(removing((EX.twist, GC["as-seen-by"], EX.frame1),
                  (EX.inertia, RC["as-seen-by"], EX.frame1),
                  (EX.wrench, RC["as-seen-by"], EX.frame1))),             # 1 and 2 hold, the rest too
    call(removing((EX.inertiaRel, RE["about"], EX.point1),
                  (EX.velocityRel, GR["reference-point"], EX.point1),
                  (EX.wrenchRel, RE["reference-point"], EX.point1))),     # 3 and 4: None == None
    # two values for the inertia's as-seen-by: the first read is compared
    call(adding((EX.inertia, RC["as-seen-by"], EX.frame2))),
    call(both(removing((EX.inertia, RC["as-seen-by"], EX.frame1)),
              adding((EX.inertia, RC["as-seen-by"], EX.frame2),
                     (EX.inertia, RC["as-seen-by"], EX.frame1)))),
    # the namespace of as-seen-by matters
    call(both(removing((EX.inertia, RC["as-seen-by"], EX.frame1),
                       (EX.wrench, RC["as-seen-by"], EX.frame1)),
              adding((EX.inertia, GC["as-seen-by"], EX.frame1),
                     (EX.wrench, GC["as-seen-by"], EX.frame1)))),
    call(lambda g: g.remove((None, None, None))),                  # empty graph
    # subjects passed in that the graph does not know
    call(args=(EX.unknown1, EX.unknown2, EX.unknown3)),
]

VERDICT = run_pair(
    __file__,
    entry="inertial_wrench",
    calls=CALLS,
    fixture=None,
)
