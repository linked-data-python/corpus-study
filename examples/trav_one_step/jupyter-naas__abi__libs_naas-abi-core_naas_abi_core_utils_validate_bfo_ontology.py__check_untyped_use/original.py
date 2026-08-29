# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: check_untyped_use (lines 1149-1238, stratum trav_one_step)
# licence of the source repository: see meta.json
def check_untyped_use(g: Graph) -> list[dict]:
    issues = []
    KNOWN_PREFIXES = (
        "http://purl.obolibrary.org/obo/",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "http://www.w3.org/2000/01/rdf-schema#",
        "http://www.w3.org/2002/07/owl#",
        "http://www.w3.org/2004/02/skos/core#",
        "http://purl.org/dc/",
        "https://www.commoncoreontologies.org/",
    )

    declared_classes = {
        s for s in g.subjects(RDF.type, OWL.Class) if isinstance(s, URIRef)
    }
    declared_classes |= {
        s for s in g.subjects(RDF.type, RDFS.Class) if isinstance(s, URIRef)
    }
    declared_properties = {
        s for s in g.subjects(RDF.type, OWL.ObjectProperty) if isinstance(s, URIRef)
    }
    declared_properties |= {
        s for s in g.subjects(RDF.type, OWL.DatatypeProperty) if isinstance(s, URIRef)
    }
    declared_properties |= {
        s for s in g.subjects(RDF.type, RDF.Property) if isinstance(s, URIRef)
    }

    def _is_vocab(iri: URIRef) -> bool:
        return any(str(iri).startswith(p) for p in KNOWN_PREFIXES)

    class_uses: set[URIRef] = set()
    for o in g.objects(None, RDFS.subClassOf):
        if isinstance(o, URIRef):
            class_uses.add(o)
    for o in g.objects(None, RDF.type):
        if isinstance(o, URIRef):
            class_uses.add(o)
    for pred in (
        OWL.allValuesFrom,
        OWL.someValuesFrom,
        OWL.unionOf,
        OWL.intersectionOf,
    ):
        for o in g.objects(None, pred):
            if isinstance(o, URIRef):
                class_uses.add(o)

    for iri in class_uses:
        if _is_vocab(iri):
            continue
        if iri not in declared_classes and iri not in declared_properties:
            issues.append(
                {
                    "severity": "WARNING",
                    "category": "UNTYPED_USE",
                    "subject": _short(iri, g),
                    "message": (
                        f"'{iri}' is used in a class position (subClassOf, rdf:type, "
                        f"or restriction filler) but is never declared as owl:Class."
                    ),
                }
            )

    prop_uses: set[URIRef] = set()
    for o in g.objects(None, OWL.onProperty):
        if isinstance(o, URIRef):
            prop_uses.add(o)
    for pred in (RDFS.domain, RDFS.range):
        for s in g.subjects(pred, None):
            if isinstance(s, URIRef):
                prop_uses.add(s)

    for iri in prop_uses:
        if _is_vocab(iri):
            continue
        if iri not in declared_properties and iri not in declared_classes:
            issues.append(
                {
                    "severity": "WARNING",
                    "category": "UNTYPED_USE",
                    "subject": _short(iri, g),
                    "message": (
                        f"'{iri}' is used in a property position (onProperty, "
                        f"domain, or range) but is never declared as owl:ObjectProperty "
                        f"or owl:DatatypeProperty."
                    ),
                }
            )
    return issues
