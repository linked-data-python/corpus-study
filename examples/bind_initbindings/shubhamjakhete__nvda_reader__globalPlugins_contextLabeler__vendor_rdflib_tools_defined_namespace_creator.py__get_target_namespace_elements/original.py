# Extracted from shubhamjakhete/nvda_reader@8b5fb51e42 : globalPlugins/contextLabeler/_vendor/rdflib/tools/defined_namespace_creator.py
# region: get_target_namespace_elements (lines 75-112, stratum bind_initbindings)
# licence of the source repository: see meta.json
from typing import TYPE_CHECKING, Iterable, List, Tuple
from rdflib.graph import Graph  # noqa: E402
from rdflib.namespace import DCTERMS, OWL, RDFS, SKOS  # noqa: E402

def get_target_namespace_elements(
    g: Graph, target_namespace: str
) -> Tuple[List[Tuple[str, str]], List[str]]:
    namespaces = {"dcterms": DCTERMS, "owl": OWL, "rdfs": RDFS, "skos": SKOS}
    q = """
        SELECT ?s (GROUP_CONCAT(DISTINCT STR(?def)) AS ?defs)
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
        GROUP BY ?s
        """.replace(
        "xxx", target_namespace
    )
    elements: List[Tuple[str, str]] = []
    for r in g.query(q, initNs=namespaces):
        if TYPE_CHECKING:
            assert isinstance(r, ResultRow)
        elements.append((str(r[0]), str(r[1])))

    elements.sort(key=lambda tup: tup[0])

    elements_strs: List[str] = []
    for e in elements:
        desc = e[1].replace("\n", " ")
        elements_strs.append(
            f"    {e[0].replace(target_namespace, '')}: URIRef  # {desc}\n"
        )

    return elements, elements_strs
