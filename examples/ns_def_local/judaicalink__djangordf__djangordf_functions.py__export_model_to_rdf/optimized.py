# Extracted from judaicalink/djangordf@494eedbeba : djangordf/functions.py
# region: export_model_to_rdf (lines 13-91, stratum ns_def_local)
# licence of the source repository: see meta.json
import os
import logging
from datetime import datetime
from context_shim import settings  # context shim -- see meta.json
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
logger = logging.getLogger(__name__)

def export_model_to_rdf(model, dump_name, namespace=None, output_dir=None):
    """Export all instances of a Django model to a Turtle RDF file.

    Each instance becomes a subject identified by its primary key. Each
    model field becomes a predicate; values are emitted as typed literals.

    :param model: Django model class to export.
    :param dump_name: Logical name used in the file name and dump metadata.
    :param namespace: Optional base IRI. Defaults to
        ``http://example.org/<modelname>/``.
    :param output_dir: Directory the Turtle file is written to. Defaults
        to ``settings.BASE_DIR``.
    :returns: Absolute path of the written Turtle file.
    """
    ns = Namespace(namespace or f"http://example.org/{model.__name__.lower()}/")
    g = Graph()
    g.bind(model.__name__.lower(), ns)

    for instance in model.objects.all():
        subject_uri = ns[str(instance.pk)]
        g.add((subject_uri, RDF.type, ns[model.__name__]))
        for field in model._meta.fields:
            field_value = getattr(instance, field.name)
            if field_value is None:
                continue
            # bool must be checked before int: bool is a subclass of int.
            for kind, datatype in ((bool, XSD.boolean), (int, XSD.integer), (float, XSD.float),
                                   (datetime, XSD.dateTime), (str, XSD.string)):
                if isinstance(field_value, kind):
                    g.add((subject_uri, ns[field.name], Literal(field_value, datatype=datatype)))
                    break
            else:
                logger.warning("Unhandled field type %s for %s.%s; skipping.",
                               type(field_value).__name__, model.__name__, field.name)

    g += [(ns.dump_metadata, RDF.type, ns.DumpMetadata),
          (ns.dump_metadata, ns.dump_name, Literal(dump_name, datatype=XSD.string)),
          (ns.dump_metadata, ns.timestamp, Literal(datetime.now(), datatype=XSD.dateTime))]

    dump_file_path = os.path.join(output_dir or settings.BASE_DIR,
                                  f"{dump_name}_{datetime.now():%Y%m%d_%H%M%S}.ttl")
    with open(dump_file_path, "w", encoding="utf-8") as f:
        f.write(g.serialize(format="turtle"))

    return dump_file_path
