# Extracted from mapsa/blathers@cad7822217 : tests/test_classifier.py
# region: test_classify_with_regex_label (lines 74-86, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from blathers.classifier import classify
SHAPES = [FIXTURES / "flag-shapes.ttl"]
SYS = Namespace("https://example.com/sys#")
VOC = Namespace("https://example.com/voc#")
EX = Namespace("https://example.com/instances#")
FLAGGED_UNDER = URIRef("https://example.com/ns#flaggedUnder")

def test_classify_with_regex_label():
    from blathers.classifier import make_regex_label

    g = _data_graph()
    classify(
        g,
        SHAPES,
        target_property=FLAGGED_UNDER,
        class_as_value_props=[SYS.hasPurpose],
        class_value_namespaces=[str(VOC)],
        shape_label=make_regex_label(r"^Risky(\w+)Shape$", r"risk: \1"),
    )
    assert list(g.objects(EX.RiskyWidget, FLAGGED_UNDER)) == [Literal("risk: Purpose")]
