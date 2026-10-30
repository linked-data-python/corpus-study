"""Validation driver for llhhx0826__swrl2rdf__tests_test_builder.py__test_rule_label_written_as_rdfs_label.

The region's whole effect is an internal ``assert``: it returns None or
raises, and the harness compares raises (type and message).  The only
argument is ``prefix_map``.  Each call passes ONE ``PrefixMap`` instance to
both sides (a factory that returns the same object twice), because
``PrefixMap`` has no ``__eq__``: two equal-by-content instances would be
reported as differing by identity.  Sharing is safe since ``rules_to_graph``
only reads it.

What the region decides depends on the graph that ``rules_to_graph`` builds
INSIDE the region, and the real builder always writes exactly one swrl:Imp
with exactly one rdfs:label.  To reach the other cases, this driver opens a
seam: it replaces ``swrl2rdf_shim.rules_to_graph`` -- before the harness
executes either side, so both sides import the same wrapper -- with one that
calls the real builder unchanged, then applies the edit registered for the
``PrefixMap`` instance of the current call.  The region's text is untouched,
and both sides receive the same graph for the same call.  A call with no
registered edit gets the real graph.

Calls, and what each one exercises:

0. ``PrefixMap()``, real graph: one Imp, label "Rule_0" -> returns None.
1. ``PrefixMap({"ex": "http://example.org/"})``, the instance the
   repository's ``prefix_map`` fixture builds (tests/conftest.py), real
   graph -> returns None.
2. no swrl:Imp at all (its rdf:type triple removed; the node keeps its
   label): ``next()`` raises StopIteration -- the zero-solution case.
3. no swrl:Imp, but the labelled node points to swrl:Imp through
   rdfs:seeAlso: a pattern widened to ``?imp ?p swrl:Imp`` would find it and
   pass, where the original raises StopIteration.
4. two swrl:Imp nodes, the second labelled "Other": ``next()`` takes the
   first and does not raise; ``.one()`` would raise ValueError.
5. the Imp has no rdfs:label, and another node of the graph (the body list)
   carries rdfs:label "Rule_0": ``g.value`` gives None, ``str(None)`` is
   "None", the assert fails; a label pattern widened to ``?s rdfs:label
   ?label`` would pass.
6. the Imp has two rdfs:label values ("Rule_0" and "Other"): ``g.value``
   takes the first and does not raise; ``.one()`` would raise ValueError.
7. the label is the empty literal ``""`` (falsy, present): ``str`` gives "",
   the assert fails on both sides.
8. the label carries a language tag, ``"Rule_0"@en``: ``str`` drops it, the
   assert holds on both sides.
"""
from rdflib import BNode, Literal, Namespace, RDF, RDFS

import swrl2rdf_shim
from rdfeval.harness import run_pair
from swrl2rdf_shim import PrefixMap

SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
EX_NS = "http://example.org/"          # tests/conftest.py, EX_NS

_real_rules_to_graph = swrl2rdf_shim.rules_to_graph
EDITS = {}                              # PrefixMap instance -> graph edit


def rules_to_graph(rules, prefix_map, graph=None):
    """The real builder, then the edit registered for this call, if any."""
    g = _real_rules_to_graph(rules, prefix_map, graph)
    edit = EDITS.get(prefix_map)
    if edit is not None:
        edit(g)
    return g


swrl2rdf_shim.rules_to_graph = rules_to_graph


def _imp(g):
    (imp,) = g.subjects(RDF.type, SWRL.Imp)
    return imp


def no_imp(g):
    g.remove((_imp(g), RDF.type, SWRL.Imp))


def no_imp_see_also(g):
    imp = _imp(g)
    g.remove((imp, RDF.type, SWRL.Imp))
    g.add((imp, RDFS.seeAlso, SWRL.Imp))


def two_imps(g):
    other = BNode()
    g.add((other, RDF.type, SWRL.Imp))
    g.add((other, RDFS.label, Literal("Other")))


def label_elsewhere(g):
    imp = _imp(g)
    body = g.value(imp, SWRL.body)
    g.remove((imp, RDFS.label, None))
    g.add((body, RDFS.label, Literal("Rule_0")))


def two_labels(g):
    g.add((_imp(g), RDFS.label, Literal("Other")))


def empty_label(g):
    imp = _imp(g)
    g.remove((imp, RDFS.label, None))
    g.add((imp, RDFS.label, Literal("")))


def tagged_label(g):
    imp = _imp(g)
    g.remove((imp, RDFS.label, None))
    g.add((imp, RDFS.label, Literal("Rule_0", lang="en")))


def case(edit=None):
    pm = PrefixMap({"ex": EX_NS})
    if edit is not None:
        EDITS[pm] = edit
    return lambda: ((pm,), {})


VERDICT = run_pair(
    __file__,
    entry='test_rule_label_written_as_rdfs_label',
    calls=[((PrefixMap(),), {}),
           case(),
           case(no_imp),
           case(no_imp_see_also),
           case(two_imps),
           case(label_elsewhere),
           case(two_labels),
           case(empty_label),
           case(tagged_label)],
)
