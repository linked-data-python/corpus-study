# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/powerpoint/pipelines/AddPowerPointPresentationPipeline.py
# region: AddPowerPointPresentationPipeline.run (lines 148-148, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

graph.add((presentation_uri, RDF.type, OWL.NamedIndividual))
