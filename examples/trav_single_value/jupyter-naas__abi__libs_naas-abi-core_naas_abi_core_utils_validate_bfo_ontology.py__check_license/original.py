# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: check_license (lines 880-905, stratum trav_single_value)
# licence of the source repository: see meta.json
def check_license(g: Graph) -> list[dict]:
    DC = Namespace("http://purl.org/dc/terms/")
    DC11 = Namespace("http://purl.org/dc/elements/1.1/")
    issues: list[dict] = []
    onto_iri = _get_ontology_iri(g)
    if onto_iri is None:
        return issues
    has_license = (
        g.value(onto_iri, DC["license"]) is not None
        or g.value(onto_iri, DC11["license"]) is not None
        or g.value(onto_iri, URIRef("http://purl.org/dc/terms/license")) is not None
    )
    if not has_license:
        issues.append(
            {
                "severity": "WARNING",
                "category": "LICENSE_MISSING",
                "subject": _short(onto_iri, g),
                "message": (
                    f"Ontology '{onto_iri}' does not declare a license "
                    f"(dc:license or dc11:license). A license is required "
                    f"for reuse clarity."
                ),
            }
        )
    return issues
