# Extracted from DataDrivenCPS/acquirium@e3bffb4bed : src/acquirium/internals/qudt_units.py
# region: QUDTUnitConverter._search_label_contains (lines 393-401, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, XSD
from acquirium.internals.internals_namespaces import QUDT, UNIT, QUDT_QUANTITY_KIND

def _search_label_contains(self, text: str) -> UnitDefinition | None:
    target = text.casefold()
    predicates = [RDFS.label, SKOS.prefLabel, QUDT.symbol, QUDT.ucumCode, QUDT.uneceCommonCode]
    for predicate in predicates:
        for subj, _, lit in self.graph.triples((None, predicate, None)):
            if isinstance(lit, Literal) and target in str(lit).casefold():
                if self._looks_like_unit(subj):
                    return self._from_uri(subj)
    return None
