# Extracted from tteon/seocho@09f72a4569 : src/seocho/ontology/serialization.py
# region: ontology_to_ttl (lines 360-448, stratum add_in_loop)
# licence of the source repository: see meta.json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

def ontology_to_ttl(
    ontology: "Ontology",
    path: Union[str, Path],
) -> Path:
    """Write an ``Ontology`` out as Turtle.

    Inverse of :func:`ontology_from_ttl` for the OWL subset we map.
    Requires ``rdflib``.
    """
    try:
        import rdflib
        from rdflib import Literal, Namespace, OWL, RDF, RDFS, SKOS, URIRef, XSD
    except ImportError as exc:
        raise ImportError(
            "Ontology.to_ttl requires 'rdflib'. "
            "Install it with: pip install seocho[ontology]"
        ) from exc

    from .core import PropertyType

    ns_str = ontology.namespace or "https://seocho.dev/ontology/"
    if not (ns_str.endswith("/") or ns_str.endswith("#")):
        ns_str = ns_str + "/"
    ns = Namespace(ns_str)

    g = rdflib.Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)
    g.bind("priv", ns)

    onto_iri = URIRef(ns + _safe_local(ontology.name))
    g.add((onto_iri, RDF.type, OWL.Ontology))
    if ontology.description:
        g.add((onto_iri, RDFS.label, Literal(ontology.description)))

    xsd_for = {
        PropertyType.STRING: XSD.string,
        PropertyType.INTEGER: XSD.integer,
        PropertyType.FLOAT: XSD.decimal,
        PropertyType.BOOLEAN: XSD.boolean,
        PropertyType.DATETIME: XSD.dateTime,
    }

    def _cls_iri(node_label: str):
        nd = ontology.nodes.get(node_label)
        if nd is not None and nd.same_as:
            return URIRef(nd.same_as)
        return URIRef(ns + _safe_local(node_label))

    for label, node in ontology.nodes.items():
        cls_iri = URIRef(node.same_as) if node.same_as else URIRef(ns + _safe_local(label))
        g.add((cls_iri, RDF.type, OWL.Class))
        # ISO-704 surfacing: the human name is rdfs:label, the meaning/definition
        # is skos:definition (which the loader prefers). This keeps the definition
        # a first-class SKOS annotation instead of overloading rdfs:label.
        g.add((cls_iri, RDFS.label, Literal(label)))
        if node.description:
            g.add((cls_iri, SKOS.definition, Literal(node.description)))
        for alias in node.aliases or []:
            g.add((cls_iri, SKOS.altLabel, Literal(alias)))
        # Subclass hierarchy: broader -> rdfs:subClassOf (round-trips with from_ttl).
        for parent in (node.broader or []):
            if parent in ontology.nodes:
                g.add((cls_iri, RDFS.subClassOf, _cls_iri(parent)))
        for pname, p in node.properties.items():
            prop_iri = URIRef(ns + _safe_local(pname))
            g.add((prop_iri, RDF.type, OWL.DatatypeProperty))
            g.add((prop_iri, RDFS.domain, cls_iri))
            g.add((prop_iri, RDFS.range, xsd_for.get(p.property_type, XSD.string)))
            if p.description:
                g.add((prop_iri, RDFS.label, Literal(p.description)))

    for rtype, rel in ontology.relationships.items():
        prop_iri = URIRef(rel.same_as) if rel.same_as else URIRef(ns + _safe_local(rtype))
        g.add((prop_iri, RDF.type, OWL.ObjectProperty))
        if rel.description:
            g.add((prop_iri, RDFS.label, Literal(rel.description)))
        if rel.source and rel.source != "Any":
            g.add((prop_iri, RDFS.domain, URIRef(ns + _safe_local(rel.source))))
        if rel.target and rel.target != "Any":
            g.add((prop_iri, RDFS.range, URIRef(ns + _safe_local(rel.target))))
        for alias in rel.aliases or []:
            g.add((prop_iri, SKOS.altLabel, Literal(alias)))

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(out), format="turtle")
    return out
