# Context shim (see meta.json): stand-ins for what surrounds
# OntologyClassifier.__init__ in JustlyAI/lmss_entity_extractor@6acc4d8389 :
# app/lmss_classification.py, so the region executes outside the package.
# Identical bindings for both representations.
#
# _load_ontology_index and _load_top_classes are transcribed VERBATIM from
# the repository (app/lmss_classification.py, lines 34-44): each just reads
# one JSON fixture beside this pair. SentenceTransformer is NOT the real
# sentence_transformers package -- it is not in the pinned study venv, and
# downloading real model weights needs network access the study does not
# have. Its return value is stored on self.model and never read again inside
# this region: the method that DOES read embeddings, _get_entity_embedding
# (not in this region), calls self.LMSS.hasEmbedding on triples already in
# self.graph, not self.model. A name-only stand-in changes nothing this pair
# observes.
#
# self.LMSS is exactly the attribute _get_entity_embedding dereferences
# elsewhere in the class (self.LMSS.hasEmbedding, self.LMSS.embeddingValue,
# lines 52-53 of the source file) -- the evidence for the translation_notes
# finding that @prefix cannot reach this site: see meta.json.
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SentenceTransformer:
    def __init__(self, model_name):
        self.model_name = model_name


class OntologyClassifier:
    """Only what __init__ needs on self before it runs: nothing. The
    constructor under test (original.py / translated.ldpy's free-standing
    __init__) is called on a bare instance of this class from demo()."""

    def _load_ontology_index(self, index_path: str) -> List[Dict[str, Any]]:
        with open(index_path, "r") as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} entities from index")
        return data

    def _load_top_classes(self, top_classes_path: str) -> Dict[str, str]:
        with open(top_classes_path, "r") as f:
            top_classes_data = json.load(f)
        top_classes = {cls["iri"]: cls["label"] for cls in top_classes_data}
        logger.info(f"Loaded {len(top_classes)} top classes from {top_classes_path}")
        return top_classes
