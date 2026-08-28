# Extracted from tteon/seocho@09f72a4569 : examples/teaching/_shared/compat.py
# region: load_ontology_from_ttl (lines 219-309, stratum trav_one_step)
# licence of the source repository: see meta.json
from typing import Any, Dict, List, Optional, Set

def load_ontology_from_ttl(path: str | Any) -> Any:
    """Load an OWL/SKOS TTL file into a ``seocho.ontology.Ontology``.

    ``seocho.Ontology`` does not expose a TTL loader (only YAML / JSON-LD /
    dict / artifact). This helper parses the Turtle with ``rdflib``, extracts
    classes (``owl:Class``), object properties (``owl:ObjectProperty``) with
    domain/range, and constructs an in-memory Ontology via
    :py:meth:`seocho.ontology.Ontology.from_dict`.

    Only ``rdfs:label`` / ``rdfs:comment`` / ``skos:definition`` /
    ``rdfs:domain`` / ``rdfs:range`` are read. Subclass hierarchy and most
    annotations are dropped — that's enough for the teaching prompts (which
    only need name + description + relationship endpoints).
    """
    try:
        import rdflib
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "load_ontology_from_ttl requires rdflib. Install via `pip install rdflib`."
        ) from exc

    from seocho.ontology import Ontology

    g = rdflib.Graph()
    g.parse(str(path), format="turtle")

    RDF = rdflib.namespace.RDF
    RDFS = rdflib.namespace.RDFS
    OWL = rdflib.namespace.OWL
    SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")

    def _local(uri: Any) -> str:
        s = str(uri)
        return s.rsplit("#", 1)[-1].rsplit("/", 1)[-1]

    def _label(uri: Any) -> str:
        for lit in g.objects(uri, RDFS.label):
            return str(lit)
        return _local(uri)

    def _description(uri: Any) -> str:
        for lit in g.objects(uri, SKOS.definition):
            return str(lit)
        for lit in g.objects(uri, RDFS.comment):
            return str(lit)
        return ""

    # Collect classes — nodes is a dict keyed by class name (seocho contract)
    nodes: Dict[str, Dict[str, Any]] = {}
    for cls in set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class)):
        if isinstance(cls, rdflib.BNode):
            continue
        name = _local(cls)
        nodes.setdefault(
            name,
            {
                "description": _description(cls),
                "properties": {},
                "aliases": [_label(cls)] if _label(cls) != name else [],
            },
        )

    # Collect object properties with domain/range — keyed by relation name
    relationships: Dict[str, Dict[str, Any]] = {}
    for prop in set(g.subjects(RDF.type, OWL.ObjectProperty)):
        domains = [_local(d) for d in g.objects(prop, RDFS.domain) if not isinstance(d, rdflib.BNode)]
        ranges = [_local(r) for r in g.objects(prop, RDFS.range) if not isinstance(r, rdflib.BNode)]
        if not (domains and ranges):
            continue
        rname = _local(prop)
        relationships.setdefault(
            rname,
            {
                "source": domains[0],
                "target": ranges[0],
                "description": _description(prop),
            },
        )
        for endpoint in (domains[0], ranges[0]):
            nodes.setdefault(
                endpoint,
                {"description": "", "properties": {}, "aliases": []},
            )

    ontology_dict: Dict[str, Any] = {
        "name": "fibo_be_minimal",
        "version": "1",
        "nodes": nodes,
        "relationships": relationships,
    }
    return Ontology.from_dict(ontology_dict)
