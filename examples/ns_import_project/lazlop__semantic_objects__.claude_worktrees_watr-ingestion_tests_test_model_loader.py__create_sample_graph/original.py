# Extracted from lazlop/semantic_objects@243c5efd8c : .claude/worktrees/watr-ingestion/tests/test_model_loader.py
# region: create_sample_graph (lines 15-75, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef
from semantic_objects.namespaces import S223, QUDT, UNIT, bind_prefixes

def create_sample_graph():
    """Create a sample RDF graph with spaces and windows for testing."""
    g = Graph()
    bind_prefixes(g)

    # Define a namespace for our test data
    EX = Namespace("http://example.org/building#")
    g.bind("ex", EX)

    # Create a Space with an Area property
    space1 = EX["Space1"]
    g.add((space1, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["Space"]))

    # Create Area property for the space
    area1 = EX["Space1_Area"]
    g.add((area1, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((area1, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Area")))
    g.add((area1, S223["hasValue"], Literal(100.0)))
    g.add((area1, QUDT["hasUnit"], UNIT["FT2"]))
    g.add((space1, S223["hasProperty"], area1))

    # Create another Space
    space2 = EX["Space2"]
    g.add((space2, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["Space"]))

    area2 = EX["Space2_Area"]
    g.add((area2, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((area2, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Area")))
    g.add((area2, S223["hasValue"], Literal(150.0)))
    g.add((area2, QUDT["hasUnit"], UNIT["M2"]))
    g.add((space2, S223["hasProperty"], area2))

    # Create a Window with multiple properties
    window1 = EX["Window1"]
    g.add((window1, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["Window"]))

    # Window area
    window_area = EX["Window1_Area"]
    g.add((window_area, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((window_area, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Area")))
    g.add((window_area, S223["hasValue"], Literal(10.0)))
    g.add((window_area, QUDT["hasUnit"], UNIT["FT2"]))
    g.add((window1, S223["hasProperty"], window_area))

    # Window azimuth
    window_azimuth = EX["Window1_Azimuth"]
    g.add((window_azimuth, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((window_azimuth, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Azimuth")))
    g.add((window_azimuth, S223["hasValue"], Literal(180.0)))
    g.add((window_azimuth, QUDT["hasUnit"], UNIT["DEG"]))
    g.add((window1, S223["hasProperty"], window_azimuth))

    # Window tilt
    window_tilt = EX["Window1_Tilt"]
    g.add((window_tilt, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), S223["QuantifiableObservableProperty"]))
    g.add((window_tilt, QUDT["hasQuantityKind"], URIRef("http://qudt.org/vocab/quantitykind/Tilt")))
    g.add((window_tilt, S223["hasValue"], Literal(90.0)))
    g.add((window_tilt, QUDT["hasUnit"], UNIT["DEG"]))
    g.add((window1, S223["hasProperty"], window_tilt))

    return g
