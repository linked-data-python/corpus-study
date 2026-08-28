# Extracted from RDFLib/prez@421ee0a9fe : prez/services/app_service.py
# region: retrieve_local_queryable_definitions (lines 305-335, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, RDF, SH, BNode, Graph, Literal, URIRef
from prez.cache import (
    counts_graph,
    endpoints_graph_cache,
    prefix_graph,
    prez_system_graph,
)
from prez.config import settings, get_reference_data_dir
log = logging.getLogger(__name__)

async def retrieve_local_queryable_definitions(app_state, system_store):
    """
    Loads local queryable definitions from files into the system store.
    """
    queryables_dir = get_reference_data_dir() / "queryables"
    g = Graph()
    files = list(queryables_dir.glob("*.ttl")) + list(queryables_dir.glob("*.rdf"))
    for f in files:
        g.parse(f)
    if len(g) > 0:
        prez_system_graph.__iadd__(g)
        queryable_bytes = g.serialize(format="nt", encoding="utf-8")
        system_store.load(queryable_bytes, "application/n-triples")
        queryables = list(
            g.subjects(
                predicate=RDF.type,
                object=URIRef("http://www.opengis.net/doc/IS/cql2/1.0/Queryable"),
            )
        )
        for triple in list(g.triples_choices((queryables, DCTERMS.identifier, None))):
            app_state.queryable_props[str(triple[2])] = str(triple[0])
        n_queryables = len(queryables)
        names_list = [
            f'"{str(triple[2])}"'
            for triple in g.triples_choices((queryables, SH.name, None))
        ]
        log.info(
            f'Found and added {n_queryables} local queryables: {", ".join(names_list)}'
        )
    else:
        log.info("No local queryable definitions found")
