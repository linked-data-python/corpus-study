# Extracted from BrickSchema/Brick@c12949f236 : tests/test_inference.py
# region: test_virtual_meter1 (lines 209-214, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import RDF, RDFS, OWL, Namespace, Literal
from bricksrc.namespaces import BRICK, TAG, A, SKOS  # noqa: E402
BLDG = Namespace("https://brickschema.org/schema/ExampleBuilding#")

def test_virtual_meter1(brick_with_imports):
    g = brick_with_imports
    g.add((BLDG.abcdef, A, BRICK.Electrical_Meter))
    g.add((BLDG.abcdef, BRICK.isVirtualMeter, [(BRICK.value, Literal(True))]))
    valid, _, report = g.validate(engine="topquadrant")
    assert valid, report
