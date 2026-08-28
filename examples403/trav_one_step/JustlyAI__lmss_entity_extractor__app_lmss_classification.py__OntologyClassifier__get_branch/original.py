# Extracted from JustlyAI/lmss_entity_extractor@6acc4d8389 : app/lmss_classification.py
# region: OntologyClassifier._get_branch (lines 161-171, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, RDFS, Literal
logger = logging.getLogger(__name__)

def _get_branch(self, entity_iri: str) -> str:
    logger.info(f"Getting branch for entity: {entity_iri}")
    for parent in self.graph.transitive_objects(
        URIRef(entity_iri), RDFS.subClassOf
    ):
        logger.info(f"Checking parent: {parent}")
        if str(parent) in self.top_classes:
            logger.info(f"Found top class: {self.top_classes[str(parent)]}")
            return self.top_classes[str(parent)]
    logger.warning(f"No branch found for entity: {entity_iri}")
    return "Unknown"
