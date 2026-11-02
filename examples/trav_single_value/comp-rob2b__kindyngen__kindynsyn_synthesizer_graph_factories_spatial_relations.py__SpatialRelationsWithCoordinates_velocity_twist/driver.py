"""Validation driver for comp-rob2b__kindyngen__kindynsyn_synthesizer_graph_factories_spatial_relations.py__SpatialRelationsWithCoordinates_velocity_twist.

`velocity_twist(self, of, wrt, as_seen_by, reference_point=None, ang=None,
lin=None)` asserts that `as_seen_by` is a Frame, defaults a falsy
`reference_point` to the frame's origin (`g.value(frame, origin)`), then
delegates to two collaborators it does not own: `self.rel.velocity(...)` and
`self.coord.velocity_twist(...)`.  The driver gives it:

  * `rel.g`, a `ReadLog`: a real rdflib Graph read from fixture.ttl whose
    `triples()` records the (subject, predicate) of every pattern the REGION
    asks (the record lives in `self.reads`, an attribute of `self`, so the
    harness compares it with the other mutations).  `o in g[s:p]` scans the
    objects of (s, p), the island's existence test asks (s, p, o) directly:
    the same question, hence the object position is left out of the record.
  * `rel` and `coord` stand-ins that record their calls (`self.reads` as
    well) and return values built from their arguments, so that what the
    region computed (the defaulted reference point above all) reaches the
    return value and the recorded calls.  A falsy value that is not None
    (an empty IRI) is passed too: `if not reference_point` is on truthiness.

Calls: a frame with an origin, with none (the default is None), with two
(the first read wins), a non-Frame that has an origin (AssertionError), a
frame whose origin sits under another predicate, a reference point given
(no read at all), falsy reference points (None, an empty URIRef, 0), the
angular/linear arguments passed through, and an empty graph.
"""
import sys
from pathlib import Path
from urllib.parse import quote

from rdflib import Graph, Namespace, URIRef

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
EX = Namespace("http://example.org/")


def _in_region(name="velocity_twist"):
    """True while the region's function is on the stack: the harness itself
    reads the argument graph after the call, and that is not the region."""
    f = sys._getframe(2)
    while f is not None:
        if f.f_code.co_name == name:
            return True
        f = f.f_back
    return False


class ReadLog(Graph):
    def __init__(self, reads, *a, **kw):
        super().__init__(*a, **kw)
        self._reads = reads

    def triples(self, triple):
        if _in_region():
            self._reads.append(("ask", triple[0], triple[1]))
        yield from super().triples(triple)


class Rel:
    def __init__(self, reads, empty):
        self.g = ReadLog(reads)
        if not empty:
            self.g.parse(source=str(FIXTURE), format="turtle")
        self._reads = reads

    def velocity(self, of, with_respect_to, reference_point):
        self._reads.append(("rel.velocity", of, with_respect_to, reference_point))
        return URIRef("urn:velocity:" + quote("%s|%s|%s" % (of, with_respect_to, reference_point), safe=""))


class Coord:
    def __init__(self, reads):
        self._reads = reads

    def velocity_twist(self, of_velocity, as_seen_by, angular_velocity, linear_velocity):
        self._reads.append(("coord.velocity_twist", of_velocity, as_seen_by,
                            angular_velocity, linear_velocity))
        return ("twist", of_velocity, as_seen_by, angular_velocity, linear_velocity)


class Self:
    """Stand-in for SpatialRelationsWithCoordinates: `.rel` and `.coord`."""

    def __init__(self, empty=False):
        self.reads = []
        self.rel = Rel(self.reads, empty)
        self.coord = Coord(self.reads)


def call(*args, empty=False, **kwargs):
    def c():
        return ((Self(empty),) + args, kwargs)
    return c


BODY, WRT = EX.bodyA, EX.bodyB
CALLS = [
    call(BODY, WRT, EX.frame1),                                   # origin read: point1
    call(BODY, WRT, EX.frame2),                                   # no origin: None
    call(BODY, WRT, EX.frame3),                                   # two origins: first read
    call(BODY, WRT, EX.notframe),                                 # not a Frame: AssertionError
    call(BODY, WRT, EX.frame4),                                   # origin under another predicate: None
    call(BODY, WRT, EX.point1),                                   # a Point, not a Frame
    call(BODY, WRT, EX.unknown),                                  # not in the graph
    call(BODY, WRT, EX.frame1, EX.given),                         # reference point given: no read of the origin
    call(BODY, WRT, EX.frame1, reference_point=EX.given),
    call(BODY, WRT, EX.frame1, None),                             # explicitly None
    call(BODY, WRT, EX.frame1, URIRef("")),                       # falsy URIRef: defaulted
    call(BODY, WRT, EX.frame1, 0),                                # falsy 0: defaulted
    call(BODY, WRT, EX.frame1, "x"),                              # truthy: kept
    call(BODY, WRT, EX.frame1, None, "ang", "lin"),               # extra arguments pass through
    call(BODY, WRT, EX.frame3, angular_velocity="a", linear_velocity="l"),
    call(BODY, WRT, EX.frame1, empty=True),                       # empty graph: AssertionError
]

VERDICT = run_pair(
    __file__,
    entry="velocity_twist",
    calls=CALLS,
    fixture=None,
)
