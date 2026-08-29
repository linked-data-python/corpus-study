# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: _collect_all_restrictions._walk (lines 723-757, stratum trav_existence)
# licence of the source repository: see meta.json
def _walk(c: URIRef) -> None:
    if c in visited_classes:
        return
    visited_classes.add(c)
    for parent in g.objects(c, RDFS.subClassOf):
        if isinstance(parent, BNode):
            if g.value(parent, RDF.type) == OWL.Restriction:
                on_prop = g.value(parent, OWL.onProperty)
                if not isinstance(on_prop, URIRef):
                    continue
                avf = g.value(parent, OWL.allValuesFrom)
                svf = g.value(parent, OWL.someValuesFrom)
                if avf is not None:
                    quantifier, filler = (
                        "allValuesFrom",
                        avf if isinstance(avf, URIRef) else None,
                    )
                elif svf is not None:
                    quantifier, filler = (
                        "someValuesFrom",
                        svf if isinstance(svf, URIRef) else None,
                    )
                else:
                    quantifier, filler = "other", None
                restrictions.append(
                    {
                        "cls": c,
                        "on_prop": on_prop,
                        "quantifier": quantifier,
                        "filler": filler,
                        "bnode": parent,
                    }
                )
        elif isinstance(parent, URIRef):
            _walk(parent)
