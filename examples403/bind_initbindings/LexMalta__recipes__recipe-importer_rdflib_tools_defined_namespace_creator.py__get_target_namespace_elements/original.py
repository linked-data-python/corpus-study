# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/tools/defined_namespace_creator.py
# region: get_target_namespace_elements (lines 69-101, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.namespace import DCTERMS, OWL, RDFS, SKOS
from lexmalta_context import args

def get_target_namespace_elements(g, target_namespace):
    namespaces = {"dcterms": DCTERMS, "owl": OWL, "rdfs": RDFS, "skos": SKOS}
    q = """
        SELECT DISTINCT ?s ?def
        WHERE {
            # all things in the RDF data (anything RDF.type...)
            ?s a ?o .

            # get any definitions, if they have one
            OPTIONAL {
                ?s dcterms:description|rdfs:comment|skos:definition ?def
            }

            # only get results for the target namespace (supplied by user)
            FILTER STRSTARTS(STR(?s), "xxx")
        }
        """.replace(
        "xxx", target_namespace
    )
    elements = []
    for r in g.query(q, initNs=namespaces):
        elements.append((str(r[0]), str(r[1])))

    elements.sort(key=lambda tup: tup[0])

    elements_strs = []
    for e in elements:
        desc = e[1].replace("\n", " ")
        elements_strs.append(
            f"    {e[0].replace(args.target_namespace, '')}: URIRef  # {desc}\n"
        )

    return elements, elements_strs
