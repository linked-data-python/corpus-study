# Extracted from BrickSchema/Brick@c12949f236 : tests/test_subclass_hierarchy.py
# region: test_cycles (lines 18-40, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph
from context_shim import minify  # context shim, see meta.json

g = Graph()

def test_cycles(g=g):
    # Find all the classes that make the hierarchy cyclic.
    classes_in_cycles = g.query(
        "SELECT ?brick_class WHERE { ?brick_class rdfs:subClassOf+ ?brick_class .}"
    )

    # Find all the triples involved.
    loops = set()
    for (brick_class,) in classes_in_cycles:
        res2 = g.query("""SELECT ?s ?o WHERE {{
            ?s rdfs:subClassOf ?o .
            brick:{0} rdfs:subClassOf+ ?s .
            ?o rdfs:subClassOf+ brick:{0} .
        }}""".format(minify(brick_class)))
        loops.update("%s -> subClassOf -> %s" % (minify(s), minify(o)) for s, o in res2)
    assert not loops, f"Loops found in the class hierarchy! {loops}"
