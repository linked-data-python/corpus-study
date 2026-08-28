# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/generate-term-index.py
# region: main (lines 110-153, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Namespace, RDF, RDFS, OWL, URIRef
from rdflib.namespace import SKOS
ROOT = Path(__file__).resolve().parents[1]
PROPERTY_TYPES = {
    OWL.ObjectProperty: "object",
    OWL.DatatypeProperty: "data",
    OWL.AnnotationProperty: "annotation",
}

for module in modules:
    module_id = module["id"]
    graph = Graph().parse(ROOT / module["source"]["path"], format="turtle")

    for subject in set(graph.subjects(RDF.type, OWL.Class)):
        name = shorten(subject) if isinstance(subject, URIRef) else None
        if not name or name in seen:
            continue
        seen.add(name)
        parents = sorted(
            filter(None, (shorten(p) for p in graph.objects(subject, RDFS.subClassOf)))
        )
        classes.append((name, module_id, ", ".join(parents), summarize(graph, subject)))

    for owl_type, kind in PROPERTY_TYPES.items():
        for subject in set(graph.subjects(RDF.type, owl_type)):
            name = shorten(subject) if isinstance(subject, URIRef) else None
            if not name or name in seen:
                continue
            seen.add(name)
            domain = next(graph.objects(subject, RDFS.domain), None)
            rng = next(graph.objects(subject, RDFS.range), None)
            signature = " → ".join(
                label_of(graph, n) if n is not None else "—" for n in (domain, rng)
            )
            properties.append((name, kind, module_id, signature, summarize(graph, subject)))

    for subject in set(graph.subjects(RDF.type, SKOS.Concept)):
        name = shorten(subject) if isinstance(subject, URIRef) else None
        if not name or name in seen:
            continue
        seen.add(name)
        categories = sorted(
            filter(
                None,
                (
                    shorten(t)
                    for t in graph.objects(subject, RDF.type)
                    if t not in (SKOS.Concept, OWL.NamedIndividual)
                ),
            )
        )
        notation = next(graph.objects(subject, SKOS.notation), "")
        concepts.append((name, ", ".join(categories), module_id, str(notation)))
