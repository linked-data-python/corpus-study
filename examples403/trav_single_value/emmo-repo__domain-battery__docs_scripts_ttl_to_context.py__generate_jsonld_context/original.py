# Extracted from emmo-repo/domain-battery@9891630af6 : docs/scripts/ttl_to_context.py
# region: generate_jsonld_context (lines 10-95, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from rdflib.namespace import RDF, OWL, SKOS

def generate_jsonld_context(ttl_file, predicate_uri, label_uri='http://www.w3.org/2000/01/rdf-schema#label'):
    """
    Generate a JSON-LD context file from a Turtle file.

    Args:
    - ttl_file: Path to the Turtle (.ttl) file.
    - predicate_uri: The URI of the predicate to map to JSON-LD.
    - label_uri: The URI for the label (default is rdfs:label).

    Returns:
    - A Python dictionary representing the JSON-LD context.
    """
    g = rdflib.Graph()
    g.parse(ttl_file, format='ttl')

    CHAMEO = rdflib.Namespace("https://w3id.org/emmo/domain/chameo#")
    g.bind('chameo', CHAMEO)

    EMMO = rdflib.Namespace("https://w3id.org/emmo#")
    g.bind('emmo', EMMO)

    context = {}
    object_properties  = {}
    other_entries = {}
    namespace_prefixes= {}
    predicate = rdflib.URIRef(predicate_uri)
    label = rdflib.URIRef(label_uri)
    existing_keys = set()

    for s, p, o in g:
        if (s, RDF.type, OWL.ObjectProperty) in g:
            # If the subject is an OWL.ObjectProperty
            label_value = g.value(s, SKOS.prefLabel)
            if label_value:
                object_properties[str(label_value)] = {
                    "@id": str(s),
                    "@type": "@id"
                }


        elif p == predicate:
            # Normal context entry
            # Use the label as key if it exists
            #label_value = g.value(s, label) if g.value(s, label) else str(s)
            label_value = str(s)
            other_entries[str(o)] = str(label_value)


    # Add namespace prefixes to the context
    for prefix, uri in g.namespace_manager.namespaces():
        if len(prefix) >= 2:
            namespace_prefixes[prefix] = str(uri)

    # Sort the entries alphabetically
    sorted_object_properties = dict(sorted(object_properties.items()))
    sorted_other_entries = dict(sorted(other_entries.items()))
    sorted_namespace_prefixes = dict(sorted(namespace_prefixes.items()))

    # Merge the sorted entries
    context = {
        "@context": {
            **sorted_namespace_prefixes,
            **sorted_object_properties,
            **sorted_other_entries
        }
    }

    print("Namespaces:")
    for prefix, uri in g.namespace_manager.namespaces():
        print(f"{prefix}: {uri}")

    # Manual additions for deprecated or external terms
    manual_additions = {
        "hasNumericalValue": "https://w3id.org/emmo#EMMO_faf79f53_749d_40b2_807c_d34244c192f4",
        "hasNext": {
            "@id": "https://w3id.org/emmo#EMMO_499e24a5_5072_4c83_8625_fe3f96ae4a8d",
            "@type": "@id"
        },
        "Hold": "https://w3id.org/emmo/domain/electrochemistry#electrochemistry_f07be701_9d6a_415b_ac6d_63202297a7a1"
    }

    # Inject manual additions into context
    context["@context"].update(manual_additions)


    return context
