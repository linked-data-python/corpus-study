# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : agri_image_meta/ontology/generator.py
# region: generate_class (lines 69-123, stratum add_in_loop)
# licence of the source repository: see meta.json
import inspect
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal, BNode, XSD
from pydantic import BaseModel
from agri_image_meta.utils.namespaces import AGIMAGE, SH, DCT, FOAF, SOSA, EXIF
from agri_image_meta.utils.type_mapping import unwrap_type, python_to_xsd

def generate_class(g, model):
    """
    Generate OWL class definition from Pydantic model.

    If the model's rdf_type maps to an external vocabulary (sosa, foaf, dcat),
    emits an rdfs:subClassOf triple linking the agimage class to the external class.

    Args:
        g (Graph): RDF graph to add triples to
        model: Pydantic model class
    """
    class_name = model.__name__.replace("Metadata", "")
    class_uri = AGIMAGE[class_name]

    g.add((class_uri, RDF.type, OWL.Class))

    # Add rdfs:subClassOf when rdf_type points to an external vocabulary
    rdf_type_default = model.model_fields.get("rdf_type")
    if rdf_type_default is not None:
        external_uri = _resolve_rdf_type_uri(rdf_type_default.default)
        if external_uri is not None:
            g.add((class_uri, RDFS.subClassOf, external_uri))

    for field_name, field in model.model_fields.items():
        extra = field.json_schema_extra or {}
        uri = extra.get("uri")

        if not uri:
            continue

        prop = URIRef(uri)
        field_type = unwrap_type(field.annotation)

        # Object property (nested BaseModel)
        if inspect.isclass(field_type) and issubclass(field_type, BaseModel):
            range_class = AGIMAGE[field_type.__name__.replace("Metadata", "")]
            g.add((prop, RDF.type, OWL.ObjectProperty))
            g.add((prop, RDFS.domain, class_uri))
            g.add((prop, RDFS.range, range_class))
            generate_class(g, field_type)

        # Datatype property
        else:
            g.add((prop, RDF.type, OWL.DatatypeProperty))
            g.add((prop, RDFS.domain, class_uri))
            g.add((prop, RDFS.range, python_to_xsd(field_type)))

        g.add((prop, RDFS.label, Literal(field_name)))
        if field.description:
            g.add((prop, RDFS.comment, Literal(field.description)))

        # Add rdfs:subPropertyOf when parent_uri is specified
        parent_uri = extra.get("parent_uri")
        if parent_uri:
            g.add((prop, RDFS.subPropertyOf, URIRef(parent_uri)))
