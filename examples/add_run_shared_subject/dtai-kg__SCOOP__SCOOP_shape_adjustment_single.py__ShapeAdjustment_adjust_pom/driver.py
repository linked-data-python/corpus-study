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


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[case1, case2, case3, case4],
)
