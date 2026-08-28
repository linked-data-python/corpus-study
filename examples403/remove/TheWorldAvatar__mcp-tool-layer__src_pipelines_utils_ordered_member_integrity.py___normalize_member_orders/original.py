# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/pipelines/utils/ordered_member_integrity.py
# region: _normalize_member_orders (lines 285-371, stratum remove)
# licence of the source repository: see meta.json
from typing import Any, Optional
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

def _normalize_member_orders(
    g: Graph,
    *,
    parent: URIRef,
    collection_predicate: URIRef,
    order_predicates: list[URIRef],
    members: list[URIRef],
    messages: list[str],
) -> bool:
    changed = False
    member_infos: list[dict[str, Any]] = []
    primary_order_predicate = order_predicates[0]

    for member in members:
        order_literals: list[tuple[URIRef, Any, Optional[int]]] = []
        for predicate in order_predicates:
            for obj in g.objects(member, predicate):
                order_literals.append((predicate, obj, _parse_scalar_order(obj)))

        parsed_values = [value for _, _, value in order_literals if value is not None]
        unique_values = sorted(set(parsed_values))
        chosen_order = unique_values[0] if unique_values else None

        if len(unique_values) > 1:
            changed = True
            messages.append(
                f"Removed conflicting order values from {member}; kept scalar order {chosen_order}"
            )
        if order_literals:
            for predicate, obj, parsed in order_literals:
                if parsed != chosen_order:
                    g.remove((member, predicate, obj))
                    changed = True

        member_infos.append(
            {
                "node": member,
                "order": chosen_order,
                "score": _node_information_score(g, member, order_predicates),
            }
        )

    grouped: dict[Optional[int], list[dict[str, Any]]] = {}
    for info in member_infos:
        grouped.setdefault(info["order"], []).append(info)

    survivors: list[dict[str, Any]] = []
    for order_value, infos in grouped.items():
        if order_value is not None and len(infos) > 1:
            infos = sorted(infos, key=lambda item: item["score"], reverse=True)
            keep = infos[0]
            survivors.append(keep)
            for dropped in infos[1:]:
                g.remove((parent, collection_predicate, dropped["node"]))
                changed = True
                messages.append(
                    f"Dropped duplicate ordered member {dropped['node']} from {parent} at order {order_value}"
                )
        else:
            survivors.extend(infos)

    survivors = sorted(
        survivors,
        key=lambda item: (
            item["order"] is None,
            item["order"] if item["order"] is not None else 10**9,
            tuple(-part if isinstance(part, int) else part for part in item["score"][:-1]),
            item["score"][-1],
        ),
    )

    for new_order, info in enumerate(survivors, start=1):
        node = info["node"]
        current_values = {
            _parse_scalar_order(obj)
            for predicate in order_predicates
            for obj in g.objects(node, predicate)
        }
        if current_values != {new_order}:
            for predicate in order_predicates:
                for obj in list(g.objects(node, predicate)):
                    g.remove((node, predicate, obj))
            g.add((node, primary_order_predicate, Literal(new_order, datatype=XSD.integer)))
            changed = True
            messages.append(f"Normalized order for {node} under {parent} to {new_order}")

    return changed
