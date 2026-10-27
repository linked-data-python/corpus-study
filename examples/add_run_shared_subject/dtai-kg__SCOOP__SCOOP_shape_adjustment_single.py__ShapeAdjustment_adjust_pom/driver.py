"""Validation driver for
dtai-kg__SCOOP__SCOOP_shape_adjustment_single.py__ShapeAdjustment_adjust_pom.

`adjust_pom` is a bare method (extracted without its enclosing
`ShapeAdjustment` class): it reads/writes `self.initial_graph`,
`self.shape_path`, `self.findNS`, `self.findPS`, `self.adjusted_shape`,
`self.iterator`, `self.shaclNS`, `self.random_number`, and calls
`self.validatePath`/`self.updateShape`/`self.getConstraints`/
`self.updateCombinationShape`. `context_shim.ShapeAdjustmentStub` restores
all of it (four methods copied verbatim -- see its docstring and
meta.json).

Four independent calls, each a fresh graph/stub, exercise the branches that
matter for this stratum and for the region's control flow generally:

  1. single-path branch, a FRESH shape_identifier, with datatype, termType
     AND template_length all set, the graph pre-seeded with existing
     shacl:minLength/maxLength so the "erase then repose" pairs under
     template_length actually fire (not just the `is not None` guards).
     Exercises the two fused pairs (path+; nothing else fuses -- see
     meta.json) plus every -{ }/+{ } single-pattern pair and the m{ }.first()
     read that replaced g.value().
  2. single-path branch, TWO pom items that both match the SAME
     shape_identifier: the first pass adjusts it fresh, the second finds it
     already in self.adjusted_shape and takes the re-adjustment branch
     (self.updateShape, a verbatim copy that must correctly re-point the
     shape's own triples AND the incoming subject-side triple).
  3. the multi-path branch (len(path_list) == 2): two paths both resolve to
     the same shape_identifier_temp, self.getConstraints collects a
     pre-seeded shacl:minCount, and since constraints != {} this reaches
     self.updateCombinationShape.
  4. the len(path_list) == 1 case for a pom whose shape_path has NO match at
     all: self.findPS stays [] after the path_list loop, reaching the
     fallback block (the second `+{ }` shared-subject fusion in this
     region), including its for/else (unconditional else -- no `break` in
     the loop, so it always runs, matching the original bare-Python
     for/else exactly).

Cases 5 to 9 were added by the repair pass (triage: four green mutants of
the `-{ }` lines and of the `value is not None` guard). Each starts from a
shape that ALREADY carries shacl:path, shacl:nodeKind and shacl:datatype
(and, beside it, a neighbour shape with the same predicates that must not be
touched), and arms the guards ONE AT A TIME -- the two erasures of nodeKind
cover each other as soon as the datatype and termType guards fire together,
which is all that cases 1-4 ever do:

  5. only `datatype` is set: the nodeKind erasure under the datatype guard is
     the ONLY thing that removes the old shacl:nodeKind; the old datatype is
     replaced; no new nodeKind is written.
  6. only `termType` is set: the nodeKind erasure under the termType guard is
     the only one that fires; the OLD shacl:datatype must survive (it is
     not erased on this path).
  7. both set, on a shape that has no old nodeKind/datatype/path: the three
     erasures find nothing and the result is just the new triples.
  8. template_length set, minLength = Literal(0) and maxLength = Literal(0):
     a falsy literal is still "present" (`value is not None`), so the old
     value must be erased and replaced; `if value:` would skip it.
  9. template_length = 0 (a real value: parseRML starts it at 0) with ONLY a
     minLength present (a plain "3", so that rewriting it is visible) and no
     maxLength: the `is not None` test on template_length is not a
     truthiness test, and each of the two min/max blocks has its own guard
     (a missing maxLength writes nothing).
  10. template_length set with ONLY a maxLength present (no minLength), and
     TWO values for maxLength: the call must not fabricate a minLength.
"""
from rdflib import Graph, URIRef, Literal
from rdfeval.harness import run_pair

SHACL = "http://www.w3.org/ns/shacl#"

# Each case below is a zero-arg callable, not a plain (args, kwargs) tuple:
# run_pair invokes it ONCE PER SIDE (see its docstring), and `demo` mutates
# the graph it is given in place. A shared Graph object would let the
# original run's writes leak into the translated run's starting state
# (silently "succeeding" by comparing an already-mutated graph against
# itself) -- a fresh Graph(), rebuilt from scratch, per call, per side, is
# what actually isolates the two runs.


def case1():
    # single-path branch, a FRESH shape_identifier, with datatype, termType
    # AND template_length all set, pre-seeded with existing
    # shacl:minLength/maxLength so the "erase then repose" pairs under
    # template_length actually fire (not just the `is not None` guards).
    g = Graph()
    ps = URIRef("http://example.com/PropertyShape/name")
    g.add((ps, URIRef(SHACL + "minLength"), Literal(3)))
    g.add((ps, URIRef(SHACL + "maxLength"), Literal(10)))
    shape_path = {"http://example.com/PropertyShape/name": ["name"]}
    find_ns = [URIRef("http://example.com/NodeShape/Person")]
    pom_list = [{
        "path": [["name"]],
        "property": URIRef("http://xmlns.com/foaf/0.1/name"),
        "datatype": URIRef("http://www.w3.org/2001/XMLSchema#string"),
        "termType": URIRef(SHACL + "Literal"),
        "template_length": 5,
        "constant": False,
    }]
    return (g, shape_path, find_ns, pom_list), {}


def case2():
    # single-path branch, TWO pom items that both match the SAME
    # shape_identifier: the first pass adjusts it fresh, the second finds it
    # already in self.adjusted_shape and takes the re-adjustment branch
    # (self.updateShape, verbatim, must re-point the shape's own triples AND
    # the incoming subject-side triple).
    g = Graph()
    shape_path = {"http://example.com/PropertyShape/email": ["email"]}
    find_ns = [URIRef("http://example.com/NodeShape/Contact")]
    pom_list = [{
        "path": [["email"]],
        "property": URIRef("http://xmlns.com/foaf/0.1/mbox"),
        "datatype": None, "termType": None, "template_length": None,
        "constant": False,
    }, {
        "path": [["email"]],
        "property": URIRef("http://xmlns.com/foaf/0.1/mbox2"),
        "datatype": None, "termType": None, "template_length": None,
        "constant": False,
    }]
    return (g, shape_path, find_ns, pom_list), {}


def case3():
    # the multi-path branch (len(path_list) == 2): two paths both resolve to
    # the same shape_identifier_temp, self.getConstraints collects a
    # pre-seeded shacl:minCount, and since constraints != {} this reaches
    # self.updateCombinationShape.
    g = Graph()
    ps = URIRef("http://example.com/PropertyShape/fullname")
    g.add((ps, URIRef(SHACL + "minCount"), Literal(1)))
    shape_path = {"http://example.com/PropertyShape/fullname": ["first", "last"]}
    find_ns = [URIRef("http://example.com/NodeShape/Person")]
    pom_list = [{
        "path": [["first", "last"]],
        "property": URIRef("http://xmlns.com/foaf/0.1/fullName"),
        "datatype": None, "termType": None, "template_length": None,
        "constant": False,
    }]
    return (g, shape_path, find_ns, pom_list), {}


def case4():
    # the len(path_list) == 1 case for a pom whose shape_path has NO match
    # at all: self.findPS stays [] after the path_list loop, reaching the
    # fallback block (the second shared-subject +{ } fusion in this region),
    # including its for/else (unconditional else -- no `break` in the loop,
    # so it always runs, matching the original bare-Python for/else).
    g = Graph()
    shape_path = {}
    find_ns = [URIRef("http://example.com/NodeShape/Contact")]
    pom_list = [{
        "path": [["age"]],
        "property": URIRef("http://xmlns.com/foaf/0.1/age"),
        "datatype": URIRef("http://www.w3.org/2001/XMLSchema#integer"),
        "termType": None, "template_length": None,
        "constant": False,
    }]
    return (g, shape_path, find_ns, pom_list), {}


def _pom(**kw):
    pom = {
        "path": [["name"]],
        "property": URIRef("http://xmlns.com/foaf/0.1/name"),
        "datatype": None, "termType": None, "template_length": None,
        "constant": False,
    }
    pom.update(kw)
    return pom


def _preseeded(ps_iri, with_old=True):
    """A graph holding the target shape (old path/nodeKind/datatype) and a
    neighbour shape with the same predicates that must stay untouched."""
    g = Graph()
    for shape in ([URIRef(ps_iri)] if with_old else []) + [
            URIRef("http://example.com/PropertyShape/other")]:
        g.add((shape, URIRef(SHACL + "path"), URIRef("http://example.com/old")))
        g.add((shape, URIRef(SHACL + "nodeKind"), URIRef(SHACL + "BlankNode")))
        g.add((shape, URIRef(SHACL + "datatype"),
               URIRef("http://www.w3.org/2001/XMLSchema#integer")))
        g.add((shape, URIRef(SHACL + "minLength"), Literal(7)))
        g.add((shape, URIRef(SHACL + "maxLength"), Literal(70)))
    return g


PS = "http://example.com/PropertyShape/name"


def _single(g, pom):
    return (g, {PS: ["name"]},
            [URIRef("http://example.com/NodeShape/Person")], [pom]), {}


def case5():
    # only datatype: the nodeKind erasure under the datatype guard is alone.
    return _single(_preseeded(PS), _pom(
        datatype=URIRef("http://www.w3.org/2001/XMLSchema#string")))


def case6():
    # only termType: the nodeKind erasure under the termType guard is alone;
    # the old datatype stays.
    return _single(_preseeded(PS), _pom(termType=URIRef(SHACL + "Literal")))


def case7():
    # both set on a shape with nothing to erase (only the neighbour has it).
    return _single(_preseeded(PS, with_old=False), _pom(
        datatype=URIRef("http://www.w3.org/2001/XMLSchema#string"),
        termType=URIRef(SHACL + "Literal")))


def case8():
    # falsy-but-present literals.
    g = Graph()
    ps = URIRef(PS)
    g.add((ps, URIRef(SHACL + "minLength"), Literal(0)))
    g.add((ps, URIRef(SHACL + "maxLength"), Literal(0)))
    return _single(g, _pom(template_length=4))


def case9():
    # template_length == 0, only minLength present. The minLength is a PLAIN
    # literal "3": adding 0 to an xsd:integer 3 would rewrite the same triple
    # (a mutant `if pom["template_length"]:` could not be seen), whereas the
    # rewrite turns the plain "3" into the integer 3.
    g = Graph()
    g.add((URIRef(PS), URIRef(SHACL + "minLength"), Literal("3")))
    return _single(g, _pom(template_length=0))


def case10():
    # only maxLength present, with two values.
    g = Graph()
    g.add((URIRef(PS), URIRef(SHACL + "maxLength"), Literal(10)))
    g.add((URIRef(PS), URIRef(SHACL + "maxLength"), Literal(20)))
    return _single(g, _pom(template_length=5))


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[case1, case2, case3, case4, case5, case6, case7, case8, case9,
           case10],
)
