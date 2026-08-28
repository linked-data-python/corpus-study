# Extracted from shihanwan/memonto@65e89eac12 : memonto/core/retain.py
# region: update_memory (lines 75-145, stratum remove)
# licence of the source repository: see meta.json
import ast
from rdflib import Graph, Namespace
from memonto.llms.base_llm import LLMModel
from memonto.stores.triple.base_store import TripleStoreModel
from memonto.stores.vector.base_store import VectorStoreModel
from memonto.utils.logger import logger
from memonto.utils.rdf import (
    _render,
    find_updated_triples,
    find_updated_triples_ephemeral,
    hydrate_graph_with_ids,
)

def update_memory(
    data: Graph,
    llm: LLMModel,
    triple_store: TripleStoreModel,
    vector_store: VectorStoreModel,
    str_ontology: str,
    message: str,
    id: str,
    ephemeral: bool,
) -> str:
    if ephemeral:
        data_list = []

        for s, p, o in data:
            data_list.append(
                {
                    "s": str(s),
                    "p": str(p),
                    "o": str(o),
                }
            )

        logger.debug(f"existing memories\n{data_list}\n")

        updates = llm.prompt(
            prompt_name="update_memory",
            temperature=0.2,
            ontology=str_ontology,
            user_message=message,
            existing_memory=str(data_list),
        )
        logger.debug(f"updated memories\n{updates}\n")

        updates = ast.literal_eval(updates)
        updated_memory = find_updated_triples_ephemeral(updates, data_list)
        logger.debug(f"memories diff\n{updated_memory}\n")

        for s, p, o in data:
            for t in updated_memory:
                if str(s) == t["s"] and str(p) == t["p"] and str(o) == t["o"]:
                    data.remove((s, p, o))

        return str(updated_memory)
    else:
        matched = vector_store.search(message=message, id=id, k=3)
        logger.debug(f"existing memories\n{matched}\n")

        if not matched:
            return ""

        updates = llm.prompt(
            prompt_name="update_memory",
            temperature=0.2,
            ontology=str_ontology,
            user_message=message,
            existing_memory=str(matched),
        )

        updates = ast.literal_eval(updates)
        logger.debug(f"updated memories\n{updates}\n")

        updated_memory = find_updated_triples(original=matched, updated=updates)
        logger.debug(f"memories diff\n{updated_memory}\n")

        if not updated_memory:
            return ""

        vector_store.delete_by_ids(graph_id=id, ids=updated_memory.keys())
        triple_store.delete_by_ids(graph_id=id, ids=updated_memory.keys())

        return str(updated_memory)
