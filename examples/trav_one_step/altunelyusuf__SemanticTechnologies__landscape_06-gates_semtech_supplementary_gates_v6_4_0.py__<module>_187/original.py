# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v6_4_0.py
# region: <module> (lines 187-187, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
dc = Graph().parse(f"{HERE}/03-document/semtech_document_v6_4_0.ttl")
RO_RC = URIRef("http://example.org/rdodi/document-ontology#ReportContent")

rep = next(iter(dc.subjects(RDF.type, RO_RC)), None)
