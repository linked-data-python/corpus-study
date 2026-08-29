# Extracted from BBDFrancois/Web_Data_Project_DIA6_Royal_Family@8af66a0d48 : src/m2_kb_construction.py
# region: update_schema_and_sanitize_kb (lines 735-833, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import OWL, RDFS, XSD
from rdflib import Graph, URIRef

def update_schema_and_sanitize_kb(expanded_kb_file, ontology_file, alignment_file,
                                   output_clean_kb_file, ontology_expanded_file,
                                   alignment_expanded_file):
    """
    Full cleaning and privatisation pipeline:
      Phase 1 - Remove noisy/malformed triples
      Phase 2 - Absorb and align DBpedia properties into priv: namespace
      Phase 3 - Absorb and align DBpedia entities into priv: namespace
      Phase 4 - Rewrite the entire graph using the private vocabulary
      Phase 5 - Save updated ontology, alignment and clean KB
    """
    print("Starting Architecture Pipeline: Cleaning, Alignment and Privatisation")

    PRIV = Namespace("http://example.org/private#")
    DBO  = Namespace("http://dbpedia.org/ontology/")
    DBR  = Namespace("http://dbpedia.org/resource/")
    DBP  = Namespace("http://dbpedia.org/property/")

    kb    = Graph();  kb.parse(expanded_kb_file, format="nt")
    onto  = Graph();  onto.parse(ontology_file,  format="turtle")
    align = Graph();  align.parse(alignment_file, format="turtle")

    onto.bind("priv", PRIV);  onto.bind("owl", OWL)
    align.bind("priv", PRIV); align.bind("dbo", DBO)
    align.bind("dbr",  DBR);  align.bind("dbp", DBP); align.bind("owl", OWL)

    print(f"-> Initial graph size: {len(kb)} triples.")

    # Phase 1: Noise removal
    print("Step 1/4: Removing noisy literals and malformed URIs")
    triples_to_remove = [
        (s, p, o) for s, p, o in kb
        if (" " in str(s) or " " in str(p) or
            (isinstance(o, URIRef) and " " in str(o)) or
            (isinstance(o, Literal) and len(str(o)) > 150))
    ]
    for t in triples_to_remove:
        kb.remove(t)
    print(f"   {len(triples_to_remove)} noisy triples purged.")

    translation_map: dict = {}

    # Phase 2: Properties
    print("Step 2/4: Absorbing and aligning Properties")
    aligned_props   = {str(o): s for s, p, o in align.triples((None, OWL.equivalentProperty, None))}
    new_props_count = 0
    for s, p, o in kb:
        p_str = str(p)
        if p_str.startswith("http://dbpedia.org/ontology/") or \
           p_str.startswith("http://dbpedia.org/property/"):
            if p_str not in aligned_props:
                prop_name   = p_str.split('/')[-1]
                priv_prop   = PRIV[prop_name]
                is_obj_prop = not isinstance(o, Literal)
                onto.add((priv_prop, RDF.type,
                           OWL.ObjectProperty if is_obj_prop else OWL.DatatypeProperty))
                if not is_obj_prop:
                    onto.add((priv_prop, RDFS.range, RDFS.Literal))
                onto.add((priv_prop, RDFS.domain, OWL.Thing))
                align.add((priv_prop, OWL.equivalentProperty, URIRef(p_str)))
                aligned_props[p_str] = priv_prop
                new_props_count += 1
            translation_map[p_str] = aligned_props[p_str]

    # Phase 3: Entities
    print("Step 3/4: Absorbing and aligning Entities")
    aligned_entities   = {str(o): s for s, p, o in align.triples((None, OWL.sameAs, None))}
    new_entities_count = 0
    for node in set(kb.subjects()) | set(kb.objects()):
        node_str = str(node)
        if isinstance(node, URIRef) and node_str.startswith("http://dbpedia.org/resource/"):
            if node_str not in aligned_entities:
                priv_entity = PRIV[node_str.split('/')[-1]]
                onto.add((priv_entity, RDF.type, OWL.NamedIndividual))
                align.add((priv_entity, OWL.sameAs, URIRef(node_str)))
                aligned_entities[node_str] = priv_entity
                new_entities_count += 1
            translation_map[node_str] = aligned_entities[node_str]

    print(f"   {new_props_count} new properties and {new_entities_count} new entities added.")

    # Phase 4: Privatisation
    print("Step 4/4: Rewriting the entire graph in private vocabulary")
    clean_kb = Graph()
    for s, p, o in kb:
        new_s = translation_map.get(str(s), s)
        new_p = translation_map.get(str(p), p)
        new_o = translation_map.get(str(o), o) if isinstance(o, URIRef) else o
        clean_kb.add((new_s, new_p, new_o))

    # Phase 5: Save
    onto.serialize(destination=ontology_expanded_file,  format="turtle")
    align.serialize(destination=alignment_expanded_file, format="turtle")
    clean_kb.serialize(destination=output_clean_kb_file, format="nt")

    print("\nPipeline complete!")
    print(f"-> Final clean graph: {len(clean_kb)} triples.")
    print(f"-> Updated: {ontology_expanded_file}, {alignment_expanded_file}")
    print(f"-> New fact graph: {output_clean_kb_file}")
