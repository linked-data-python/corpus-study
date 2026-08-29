# Extracted from lazlop/semantic_objects@243c5efd8c : .claude/worktrees/semantic-subclass-fields/src/semantic_objects/exporters.py
# region: RdfExporter.generate_rdf_class_definition (lines 211-212, stratum coercion_datatype)
# licence of the source repository: see meta.json
from .namespaces import PARAM, RDF, RDFS, SH, bind_prefixes
from rdflib import Graph, Literal, BNode, URIRef

if hasattr(cls, 'label'):
    g.add((class_iri, RDFS.label, Literal(cls.label)))
