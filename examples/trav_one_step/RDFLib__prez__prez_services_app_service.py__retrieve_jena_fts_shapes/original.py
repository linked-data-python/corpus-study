# Extracted from RDFLib/prez@421ee0a9fe : prez/services/app_service.py
# region: retrieve_jena_fts_shapes (lines 105-137, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, RDF, SH, BNode, Graph, Literal, URIRef
from prez.cache import (
    counts_graph,
    endpoints_graph_cache,
    prefix_graph,
    prez_system_graph,
)
from prez.config import settings, get_reference_data_dir
from prez.reference_data.prez_ns import ONT, PREZ
from prez.repositories import Repo
log = logging.getLogger(__name__)

async def retrieve_jena_fts_shapes(repo: Repo):
    """
    Loads Jena FTS shape definitions from both remote repo and local files.
    """
    # Load remote shapes
    query = "DESCRIBE ?fts_shape WHERE {?fts_shape a <https://prez.dev/ont/JenaFTSPropertyShape>}"
    remote_g, _ = await repo.send_queries([query], [])
    if len(remote_g) > 0:
        prez_system_graph.__iadd__(remote_g)
        n_shapes = len(list(remote_g.subjects(RDF.type, ONT.JenaFTSPropertyShape)))
        names_list = list(remote_g.objects(subject=None, predicate=SH.name))
        while len(names_list) < n_shapes:
            names_list.append("(no label)")
        names = ", ".join(names_list)
        log.info(f"Found and added {n_shapes} remote Jena FTS shapes: {names}")
    else:
        log.info("No remote Jena FTS shapes found")

    # Load local shapes
    jena_fts_shapes_dir = get_reference_data_dir() / "jena_fts_shapes"
    local_g = Graph()
    for f in jena_fts_shapes_dir.glob("*.ttl"):
        local_g.parse(f, format="turtle")
    if len(local_g) > 0:
        prez_system_graph.__iadd__(local_g)
        n_shapes = len(list(local_g.subjects(RDF.type, ONT.JenaFTSPropertyShape)))
        names_list = list(local_g.objects(subject=None, predicate=SH.name))
        while len(names_list) < n_shapes:
            names_list.append("(no label)")
        names = ", ".join(names_list)
        log.info(f"Found and added {n_shapes} local Jena FTS shapes: {names}")
    else:
        log.info("No local Jena FTS shapes found")
