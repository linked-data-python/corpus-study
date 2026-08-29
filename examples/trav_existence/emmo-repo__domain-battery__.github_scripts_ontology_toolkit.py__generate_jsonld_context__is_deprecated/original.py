# Extracted from emmo-repo/domain-battery@9891630af6 : .github/scripts/ontology_toolkit.py
# region: generate_jsonld_context._is_deprecated (lines 141-142, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, OWL, SKOS, RDFS

def _is_deprecated(subject):
    return g.value(subject, OWL.deprecated) is not None
