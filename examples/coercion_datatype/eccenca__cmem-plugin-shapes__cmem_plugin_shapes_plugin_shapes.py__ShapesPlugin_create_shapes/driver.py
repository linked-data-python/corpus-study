"""Validation driver for
eccenca__cmem-plugin-shapes__cmem_plugin_shapes_plugin_shapes.py__ShapesPlugin_create_shapes.

`create_shapes` is a method (`self` an explicit first parameter), so both
sides carry an identical `demo(class_dict)` harness (see meta.json and
original.py) that builds a SimpleNamespace `self` exposing
`.shapes_graph` / `.shapes_graph_iri` / `.shapes_count` and stub
`get_class_dict`/`get_name` callables (standing in for a SPARQL SELECT and a
network call in the real plugin), calls the extracted method, and returns
`self.shapes_graph` -- comparing that graph, not the stub instance (which
would need an __eq__ for no benefit; the graph is the only observable
effect).

CALL_1 -- two classes, one property ("name") shared between them and one
inverse property ("knows") on the first class only. Exercises: node-shape
creation for both classes, the class_uuid dedup guard (not hit here --
distinct classes -- but the *property* dedup guard IS hit: "name" is added
once from Person and skipped-but-linked from Organization), the inverse
branch (SHUI.inversePath, the "<- " name prefix), sh:nodeKind's data/IRI
ternary on both branches (data=True for "name", data=False for "knows"),
and every coercion_datatype site in the region: two `Literal(x, lang="en")`
call sites (sh:name/rdfs:label, both for node shapes and property shapes)
and the `Literal("true", datatype=XSD.boolean)` site (SHUI.showAlways,
SHUI.inversePath).

CALL_2 -- an empty class_dict: the for loop's body never runs, contributing
no triple at all -- the zero-triples edge, and a check that no stray
boilerplate triple leaks into shapes_graph outside the loop.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        (
            (
                {
                    "http://example.org/data#Person": [
                        {"property": "http://example.org/data#name", "data": True, "inverse": False},
                        {"property": "http://example.org/data#knows", "data": False, "inverse": True},
                    ],
                    "http://example.org/data#Organization": [
                        {"property": "http://example.org/data#name", "data": True, "inverse": False},
                    ],
                },
            ),
            {},
        ),
        (({},), {}),
    ],
)
