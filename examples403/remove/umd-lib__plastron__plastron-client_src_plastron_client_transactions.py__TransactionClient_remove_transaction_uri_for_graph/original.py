# Extracted from umd-lib/plastron@4a7f08cc19 : plastron-client/src/plastron/client/transactions.py
# region: TransactionClient.remove_transaction_uri_for_graph (lines 185-195, stratum remove)
# licence of the source repository: see meta.json
from typing import Optional, Any
from rdflib import URIRef, Graph

def remove_transaction_uri_for_graph(self, graph: Optional[Graph]) -> Optional[Graph]:
    if graph is None:
        return None
    for s, p, o in graph:
        s_txn = self.remove_transaction_uri(s)
        o_txn = self.remove_transaction_uri(o)
        # swap the triple if either the subject or object is changed
        if s != s_txn or o != o_txn:
            graph.add((s_txn, p, o_txn))
            graph.remove((s, p, o))
    return graph
