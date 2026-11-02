# Extracted from d3fend/d3fend-ontology@cce593d61c : src/util/update_attack.py
# region: add_to_ttl (lines 401-452, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import URIRef, Literal, RDF, RDFS, Namespace
from context_shim import _xmlns as _XMLNS
from context_shim import get_framework_labels, get_deprecated_comment, ensure_superclasses
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
d3fend = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")

def add_to_ttl(tech, graph, framework="enterprise"):
    # 3 cases:
    # Not deprecated or revoked: add class, label, attack-id, subClassOf
    # Deprecated: add class, label, attack-id, subclassOf, owl:deprecated true
    # Revoked: add class, label, attack-id, subClassOf, owl:deprecated true, rdfs:seeAlso revoked_by_technique
    # Have not seen any cases of deprecated & revoked

    name = tech["label"]
    attack_id = tech["id"]
    subclass = tech["superclasses"]
    revoked_by = tech["revoked_by"]
    subtechnique = tech["data"]["x_mitre_is_subtechnique"]
    attack_uri = URIRef(_XMLNS + attack_id)
    mod_label, pref_label = get_framework_labels(name, framework)

    if pref_label is not None:
        graph.add((attack_uri, skos.prefLabel, Literal(pref_label)))

    ensure_superclasses(graph, attack_uri, subclass, framework, subtechnique)

    graph += [
        (attack_uri, RDF.type, owl.Class),
        (attack_uri, RDFS.label, Literal(mod_label)),
        (attack_uri, d3fend["attack-id"], Literal(attack_id)),
    ]
    if tech["deprecated"]:
        graph.add((attack_uri, owl.deprecated, Literal(True)))
        comment_text = get_deprecated_comment(tech, framework)
        if comment_text:
            graph.add((attack_uri, rdfs.comment, Literal(comment_text)))
        return "missing_deprecated"

    if tech["revoked"]:
        graph += [
            (attack_uri, owl.deprecated, Literal(True)),
            (attack_uri, rdfs.seeAlso, d3fend[revoked_by]),
            (attack_uri, rdfs.comment, Literal(f"This technique has been revoked by {revoked_by}")),
        ]
        return "missing_revoked"

    return "missing_neither"
