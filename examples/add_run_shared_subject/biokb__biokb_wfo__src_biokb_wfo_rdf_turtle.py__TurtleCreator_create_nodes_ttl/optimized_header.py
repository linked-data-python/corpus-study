# Extracted from biokb/biokb_wfo@67fc2c5366 : src/biokb_wfo/rdf/turtle.py
# region: TurtleCreator.create_nodes_ttl (lines 89-153, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import logging
import os.path
from rdflib import RDF, XSD, Literal
from context_shim import BASIC_NODE_LABEL, get_empty_graph, models, namespaces as ns, tqdm
logger: logging.Logger = logging.getLogger(__name__)

def create_nodes_ttl(self) -> str:
    """Create a turtle file with all nodes."""
    ttl_path = os.path.join(self.__ttls_folder, "nodes.ttl")
    logger.info("Create nodes ttl")
    graph = get_empty_graph()

    with self.Session() as session:
        for taxon in tqdm(
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
        ):
            taxon_uri = ns.WFO_NS[str(taxon.id).zfill(10)]
            graph += [
                (taxon_uri, RDF.type, ns.NODE_NS[taxon.rank.capitalize()]),
                (taxon_uri, RDF.type, ns.NODE_NS[BASIC_NODE_LABEL]),
                (taxon_uri, ns.REL_NS["name"], Literal(taxon.full_name, datatype=XSD.string)),
                (taxon_uri, ns.REL_NS["rank"], Literal(taxon.rank, datatype=XSD.string)),
                (taxon_uri, ns.REL_NS["role"], Literal(taxon.role, datatype=XSD.string)),
            ]
            if taxon.parent_id:
                graph.add((taxon_uri, ns.REL_NS["HAS_PARENT"],
                           ns.WFO_NS[str(taxon.parent_id).zfill(10)]))
            if taxon.ipni:
                graph.add((taxon_uri, ns.REL_NS["SAME_AS"], ns.IPNI_NS[str(taxon.ipni)]))

    graph.serialize(ttl_path, format="turtle")
    return ttl_path
