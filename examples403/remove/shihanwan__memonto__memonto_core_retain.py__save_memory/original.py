# Extracted from shihanwan/memonto@65e89eac12 : memonto/core/retain.py
# region: save_memory (lines 166-219, stratum remove)
# licence of the source repository: see meta.json
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

def save_memory(
    ontology: Graph,
    namespaces: dict[str, Namespace],
    data: Graph,
    llm: LLMModel,
    triple_store: TripleStoreModel,
    vector_store: VectorStoreModel,
    message: str,
    id: str,
    ephemeral: bool,
    str_ontology: str,
    updated_memory: str,
) -> None:
    relevant_memory = find_relevant_memories(
        data=data,
        vector_store=vector_store,
        message=message,
        id=id,
        ephemeral=ephemeral,
    )

    script = llm.prompt(
        prompt_name="commit_to_memory",
        temperature=0.2,
        ontology=str_ontology,
        user_message=message,
        updated_memory=updated_memory,
        relevant_memory=relevant_memory,
    )

    logger.debug(f"Retain Script\n{script}\n")

    data = _run_script(
        script=script,
        exec_ctx={"data": data} | namespaces,
        message=message,
        ontology=str_ontology,
        data=data,
        llm=llm,
    )

    logger.debug(f"Data Graph\n{data.serialize(format='turtle')}\n")

    # debug
    # _render(g=data, ns=namespaces, format="image")

    if not ephemeral:
        hydrate_graph_with_ids(data)
        triple_store.save(ontology=ontology, data=data, id=id)

        if vector_store:
            vector_store.save(g=data, ns=namespaces, id=id)

        data.remove((None, None, None))
