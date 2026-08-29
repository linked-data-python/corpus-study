# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/rdodi_procedure_audit_v4_0_0.py
# region: <module> (lines 96-96, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
dc = Graph().parse(f"{HERE}/03-document/semtech_document_v4_0_0.ttl")
doc_secs = {str(s).split("#S_")[-1]: s for cls in ("ReportSection", "ConceptSection")
            for s in dc.subjects(RDF.type, URIRef(DO + cls))}

nosrc = [k for k, s in doc_secs.items() if not dc.value(s, DCTERMS.source)]
