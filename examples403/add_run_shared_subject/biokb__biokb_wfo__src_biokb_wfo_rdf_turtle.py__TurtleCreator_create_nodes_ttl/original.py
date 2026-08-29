# Extracted from biokb/biokb_wfo@67fc2c5366 : src/biokb_wfo/rdf/turtle.py
# region: TurtleCreator.create_nodes_ttl (lines 89-153, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import logging
import os.path
from rdflib import RDF, XSD, Graph, Literal
from context_shim import (
    BASIC_NODE_LABEL,
    DB_DEFAULT_CONNECTION_STR,
    EXPORT_FOLDER,
    get_empty_graph,
    models,
    tqdm,
)
from context_shim import namespaces as ns
logger: logging.Logger = logging.getLogger(__name__)

def create_nodes_ttl(self) -> str:
    """Create a turtle file with all nodes."""
    ttl_path = os.path.join(self.__ttls_folder, "nodes.ttl")
    logger.info("Create nodes ttl")
    graph = get_empty_graph()

    with self.Session() as session:
        taxa = (
            session.query(
                models.Name.id,
                models.Name.full_name,
                models.Name.rank,
                models.Name.parent_id,
                models.Name.ipni,
                models.Name.role,
            )
            .where(
                models.Name.status == "valid",
                models.Name.parent_id.isnot(None),
                models.Name.rank.isnot(None),
                models.Name.role.in_(["accepted", "synonym"])
            )
            .all()
        )
        for taxon in tqdm(taxa):
            taxon_uri = ns.WFO_NS[str(taxon.id).zfill(10)]
            graph.add((taxon_uri, RDF.type, ns.NODE_NS[taxon.rank.capitalize()]))
            graph.add((taxon_uri, RDF.type, ns.NODE_NS[BASIC_NODE_LABEL]))

            graph.add(
                (
                    taxon_uri,
                    ns.REL_NS["name"],
                    Literal(taxon.full_name, datatype=XSD.string),
                )
            )
            graph.add(
                (
                    taxon_uri,
                    ns.REL_NS["rank"],
                    Literal(taxon.rank, datatype=XSD.string),
                )
            )
            graph.add(
                (
                    taxon_uri,
                    ns.REL_NS["role"],
                    Literal(taxon.role, datatype=XSD.string),
                )
            )
            if taxon.parent_id:
                parent_uri = ns.WFO_NS[str(taxon.parent_id).zfill(10)]
                graph.add((taxon_uri, ns.REL_NS["HAS_PARENT"], parent_uri))
            if taxon.ipni:
                ipni_uri = ns.IPNI_NS[str(taxon.ipni)]
                graph.add(
                    (
                        taxon_uri,
                        ns.REL_NS["SAME_AS"],
                        ipni_uri,
                    )
                )

    graph.serialize(ttl_path, format="turtle")
    return ttl_path
