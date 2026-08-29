# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/pipelines/utils/ordered_member_integrity.py
# region: _adopt_richer_unlinked_members_by_order (lines 528-575, stratum remove)
# licence of the source repository: see meta.json
from typing import Any, Optional
from rdflib import Graph, Literal, URIRef

def _adopt_richer_unlinked_members_by_order(
    g: Graph,
    *,
    parent: URIRef,
    contract: dict[str, Any],
    collection_predicate: URIRef,
    order_predicates: list[URIRef],
    members: list[URIRef],
    messages: list[str],
) -> tuple[list[URIRef], bool]:
    """Prefer richer same-order ordered members that were generated but not linked."""
    linked_members = {
        obj
        for _, _, obj in g.triples((None, collection_predicate, None))
        if isinstance(obj, URIRef)
    }
    unlinked_by_order: dict[int, list[URIRef]] = {}
    for candidate in _ordered_member_candidates(g, contract) - linked_members:
        order = _single_member_order(g, candidate, order_predicates)
        if order is not None:
            unlinked_by_order.setdefault(order, []).append(candidate)

    changed = False
    current_members = list(members)
    for idx, member in enumerate(list(current_members)):
        order = _single_member_order(g, member, order_predicates)
        if order is None or order not in unlinked_by_order:
            continue
        challenger = sorted(
            unlinked_by_order[order],
            key=lambda node: _node_information_score(g, node, order_predicates),
            reverse=True,
        )[0]
        if _node_information_score(g, challenger, order_predicates) <= _node_information_score(g, member, order_predicates):
            continue
        g.add((parent, collection_predicate, challenger))
        g.remove((parent, collection_predicate, member))
        current_members[idx] = challenger
        changed = True
        messages.append(
            f"Replaced linked low-information ordered member {member} with richer same-order member {challenger}"
        )
        if not list(g.triples((None, None, member))):
            continue
        if _node_information_score(g, member, order_predicates)[2] == 0:
            for triple in list(g.triples((member, None, None))):
                g.remove(triple)
    return current_members, changed
