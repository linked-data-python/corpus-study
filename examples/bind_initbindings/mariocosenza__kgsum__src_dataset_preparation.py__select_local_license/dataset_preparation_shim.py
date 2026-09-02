# Context shim (see meta.json): subset of mariocosenza/kgsum@320b14fc57's
# src/dataset_preparation.py, so the region (select_local_license) executes
# outside the module. `log_query` is called by the region but defined a few
# lines above it in the same file; transcribed verbatim. Identical for both
# representations.
import logging

logger = logging.getLogger("dataset_preparation")


def log_query(query):
    logger.info(f"SPARQL Query: {query}")
