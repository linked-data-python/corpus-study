# Extracted from JustlyAI/lmss_entity_extractor@6acc4d8389 : app/lmss_classification.py
# region: OntologyClassifier.__init__ (lines 15-32, stratum ns_def_local)
# licence of the source repository: see meta.json
from sentence_transformers import SentenceTransformer
from rdflib import Graph, URIRef, RDFS, Literal
from rdflib.namespace import Namespace
logger = logging.getLogger(__name__)

def __init__(
    self,
    graph_path: str,
    index_path: str,
    top_classes_path: str,
    similarity_threshold: float = 0.65,
    high_confidence_threshold: float = 0.9,
):
    self.graph = Graph()
    self.graph.parse(graph_path, format="turtle")
    self.ontology_entities = self._load_ontology_index(index_path)
    self.top_classes = self._load_top_classes(top_classes_path)
    self.model = SentenceTransformer("all-MiniLM-L6-v2")
    self.similarity_threshold = similarity_threshold
    self.high_confidence_threshold = high_confidence_threshold
    self.LMSS = Namespace("http://lmss.sali.org/")
    logger.info(f"Loaded {len(self.ontology_entities)} ontology entities")
    logger.info(f"Identified {len(self.top_classes)} top classes")
