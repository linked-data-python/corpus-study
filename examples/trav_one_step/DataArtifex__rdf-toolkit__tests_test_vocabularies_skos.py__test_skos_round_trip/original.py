# Extracted from DataArtifex/rdf-toolkit@226d8a1be3 : tests/test_vocabularies_skos.py
# region: test_skos_round_trip (lines 78-93, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph
from dartfx.rdf.pydantic.skos import SKOS, Collection, Concept, ConceptScheme

def test_skos_round_trip() -> None:
    """Test round-trip serialization with SKOS models."""
    concept = Concept(
        id="test",
        pref_label="Test",
        definition="A test definition",
    )

    turtle = concept.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = Concept.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == concept.model_dump()


# Test harness only (see meta.json): the region is a pytest test that only
# ever asserts, so `demo` turns a failed assertion into a comparable value
# instead of letting it abort the driver -- same convention as the
# trav_existence/trav_one_step siblings that translate a bare `test_*`
# function (see e.g. OntoUML__ontouml-json2graph, IndustryFusion__DigitalTwin
# in this same stratum). Identical on both sides.
def demo() -> object:
    try:
        test_skos_round_trip()
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
