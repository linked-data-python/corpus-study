# Extracted from RDFLib/prez@421ee0a9fe : prez/routers/management.py
# region: return_annotation_predicates (lines 110-130, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import VANN, BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from prez.config import settings
from prez.reference_data.prez_ns import PREZ

async def return_annotation_predicates():
    """
    Returns an RDF linked list of the annotation predicates used for labels, descriptions and provenance.
    """
    g = Graph()
    g.bind("prez", "https://prez.dev/")
    label_list_bn, description_list_bn, provenance_list_bn, other_list_bn = (
        BNode(),
        BNode(),
        BNode(),
        BNode(),
    )
    g.add((PREZ.AnnotationPropertyList, PREZ.labelList, label_list_bn))
    g.add((PREZ.AnnotationPropertyList, PREZ.descriptionList, description_list_bn))
    g.add((PREZ.AnnotationPropertyList, PREZ.provenanceList, provenance_list_bn))
    g.add((PREZ.AnnotationPropertyList, PREZ.otherList, other_list_bn))
    Collection(g, label_list_bn, settings.label_predicates)
    Collection(g, description_list_bn, settings.description_predicates)
    Collection(g, provenance_list_bn, settings.provenance_predicates)
    Collection(g, other_list_bn, settings.other_predicates)
    return g
