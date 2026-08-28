# Extracted from DataArtifex/rdf-toolkit@226d8a1be3 : src/dartfx/rdf/pydantic/_base.py
# region: RdfBaseModel._serialise_into_graph (lines 1335-1409, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import RDF, XSD, BNode, Graph, Literal, Namespace, URIRef

def _serialise_into_graph(
    self,
    graph: Graph,
    *,
    base_uri: str | None = None,
    rdf_uri_generator: RdfUriGenerator | None = None,
) -> URIRef | BNode:
    """Internal method to serialize this model into an RDF graph.

    Converts all annotated fields to RDF triples and adds them to the graph.
    This method handles the core serialization logic.

    Parameters
    ----------
    graph : Graph
        The rdflib Graph to add triples to.
    base_uri : str | None, optional
        Base URI for subject generation.
    rdf_uri_generator : RdfUriGenerator | None, optional
        A custom function to generate subject URIs for model instances.

    Returns
    -------
    URIRef | BNode
        The subject URI of the serialized resource.
    """
    subject = self._subject_uri(base_uri=base_uri, rdf_uri_generator=rdf_uri_generator)
    self._bind_prefixes(graph)

    rdf_type_uri = _ensure_uri(self.rdf_type)
    if rdf_type_uri is not None:
        graph.add((subject, RDF.type, rdf_type_uri))

    for name, field in self.__class__.model_fields.items():
        prop = _get_rdf_property(field)
        if prop is None:
            continue
        value = getattr(self, name)
        if value is None:
            continue
        predicate = prop.predicate_uri()

        # Fast path for LocalizedStr fields (LangStringList)
        if isinstance(value, LangStringList):
            for ls_item in value:
                graph.add(
                    (
                        subject,
                        predicate,
                        Literal(ls_item.value, lang=ls_item.lang),
                    )
                )
            continue

        is_list, _accepts_scalar, inner_type = _field_type_info(field)
        # Support both single values and lists for fields that allow both
        if is_list:
            values = value if isinstance(value, list) else [value]
        else:
            values = [value]
        for item in values:
            if item is None:
                continue

            node = self._value_to_node(
                item,
                inner_type,
                prop,
                graph,
                base_uri,
                rdf_uri_generator=rdf_uri_generator,
            )
            graph.add((subject, predicate, node))

    return subject
