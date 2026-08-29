# Extracted from mapsa/blathers@cad7822217 : src/blathers/validators/conventions.py
# region: ConventionValidator._check_metadata (lines 75-115, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS
from blathers.validators.base import Severity, ValidationResult

def _check_metadata(self) -> list[ValidationResult]:
    results = []

    ont_iri = None
    for s in self.graph.subjects(RDF.type, OWL.Ontology):
        ont_iri = s
        break

    if ont_iri is None:
        results.append(ValidationResult(
            validator="conventions",
            severity=Severity.ERROR,
            message="No owl:Ontology declaration found",
        ))
        return results

    checks = [
        (OWL.versionInfo, "version"),
        (DCTERMS.license, "license"),
        (DCTERMS.creator, "creator"),
    ]
    has_title = (
        self.graph.value(ont_iri, DCTERMS.title) is not None
        or self.graph.value(ont_iri, RDFS.label) is not None
    )
    if not has_title:
        results.append(ValidationResult(
            validator="conventions",
            severity=Severity.WARNING,
            message="Ontology missing title (dcterms:title or rdfs:label)",
        ))

    for predicate, name in checks:
        if self.graph.value(ont_iri, predicate) is None:
            results.append(ValidationResult(
                validator="conventions",
                severity=Severity.WARNING,
                message=f"Ontology missing {name} ({predicate})",
            ))

    return results
