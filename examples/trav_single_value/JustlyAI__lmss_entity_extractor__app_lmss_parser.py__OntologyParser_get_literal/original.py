# Extracted from JustlyAI/lmss_entity_extractor@6acc4d8389 : app/lmss_parser.py
# region: OntologyParser.get_literal (lines 65-66, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, BNode

def get_literal(self, s: URIRef, p: URIRef) -> str:
    return str(self.graph.value(s, p) or "")
