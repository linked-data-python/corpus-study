# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : agri_image_meta/ontology/generator.py
# region: generate_ontology (lines 126-154, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from datetime import date
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal, BNode, XSD
from agri_image_meta import __version__
from agri_image_meta.utils.namespaces import AGIMAGE, SH, DCT, FOAF, SOSA, EXIF

def generate_ontology(root_models):
    """
    Generate complete OWL ontology from a list of Pydantic models.

    Args:
        root_models (list): List of Pydantic model classes

    Returns:
        Graph: RDF graph containing the generated OWL ontology
    """
    g = Graph()

    g.bind("agimage", AGIMAGE)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("dct", DCT)
    g.bind("sosa", SOSA)
    g.bind("foaf", FOAF)
    g.bind("dcat", URIRef("http://www.w3.org/ns/dcat#"))

    g.add((AGIMAGE[""], RDF.type, OWL.Ontology))
    g.add((AGIMAGE[""], OWL.versionInfo, Literal(__version__)))
    g.add((AGIMAGE[""], DCT.created, Literal(date.today().isoformat(), datatype=XSD.date)))

    for model in root_models:
        generate_class(g, model)

    return g
