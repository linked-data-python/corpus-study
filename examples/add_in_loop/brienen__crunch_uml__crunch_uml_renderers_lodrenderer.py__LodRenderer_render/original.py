# Extracted from brienen/crunch_uml@89e871f729 : crunch_uml/renderers/lodrenderer.py
# region: LodRenderer.render (lines 433-465, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, SKOS, XSD
logger = logging.getLogger()

for model in models:
    modelname, ns = model_ns[model.id]
    for cls in model.classes:
        # First set inheritance
        for subclass in cls.subclasses:
            super_cls = class_dict.get(cls.id)
            if subclass.superclass is not None:
                sub_cls = class_dict.get(subclass.superclass.id)

                if super_cls is not None and sub_cls is not None:
                    g.add((sub_cls, RDFS.subClassOf, super_cls))

        # Then set associations
        for assoc in cls.uitgaande_associaties:
            from_cls = class_dict.get(cls.id)
            to_cls = class_dict.get(getattr(assoc.dst_class, "id", None))
            if to_cls is None:
                logger.warning(f"Doelklasse onbekend voor associatie {assoc.name or assoc.id}")
                continue

            if from_cls is not None and to_cls is not None:
                assoc_uri = (
                    ns[slugify(cls.name) + "/" + slugify(assoc.name)]
                    if assoc.name
                    else ns[slugify(cls.name) + "/" + slugify(assoc.id)]
                )
                g.add((assoc_uri, RDF.type, OWL.ObjectProperty))
                g.add((assoc_uri, RDFS.domain, from_cls))
                g.add((assoc_uri, RDFS.range, to_cls))
                g.add((assoc_uri, RDFS.label, Literal(assoc.name)))
                g.add((assoc_uri, DCTERMS.identifier, Literal(assoc.id)))
                if assoc.definitie is not None:
                    g.add((assoc_uri, RDFS.comment, Literal(assoc.definitie)))
