# Extracted from synaptixs/ontomesh@f771c8c4ee : scripts/ontology_gate.py
# region: _malformed_iris (lines 149-168, stratum trav_one_step)
# licence of the source repository: see meta.json
def _malformed_iris(graph: rdflib.Graph) -> int:
    """IRIs that are unusable: whitespace, or an unregistered bare scheme.

    Catches both known defects — ``:StatusIn progress`` (space in a prefixed
    name) and ``<fhir:MedicinalProduct>`` (the YAML prefix map is never
    expanded, so the CURIE ships as a literal IRI).
    """
    bad = set()
    known_schemes = ("http", "https", "urn", "file", "mailto", "doi", "ftp")
    for node in set(graph.all_nodes()) | set(graph.predicates()):
        if not isinstance(node, rdflib.URIRef):
            continue
        text = str(node)
        if any(ch.isspace() for ch in text):
            bad.add(text)
            continue
        scheme, sep, rest = text.partition(":")
        if sep and not rest.startswith("//") and scheme.lower() not in known_schemes:
            bad.add(text)
    return len(bad)
