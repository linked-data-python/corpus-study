# Context shim (see meta.json): subset of scripts/codegen_kg_schema.py from
# lync-cyber/CataForge@8cdf9be0d3, so the region executes outside the module.
# Identical bindings for both representations.
from collections import defaultdict
from typing import Any

import rdflib


def _blank_node_labels(graph: Any) -> dict[Any, Any] | None:
    """Deterministic blank-node labels when the graph's blank nodes form a
    forest, else ``None``.

    ShaclGenerator emits every blank node as the object of exactly one triple
    (property shapes nested under a node shape, RDF-list cells), so the blank
    nodes form a forest rooted at named subjects. For a forest, a stable label
    is a pure function of a node's rooted path plus its recursive content — no
    graph-isomorphism search needed. Returns ``None`` when that shape does not
    hold (a blank node with zero or multiple incoming edges), so the caller
    can fall back to the general canonicalizer.
    """
    bnodes = [n for n in graph.all_nodes() if isinstance(n, rdflib.BNode)]
    parents: dict[Any, Any] = {}
    for subject, predicate, obj in graph:
        if isinstance(obj, rdflib.BNode):
            if obj in parents:
                return None  # multiple incoming edges — not a forest
            parents[obj] = (subject, predicate)
    if any(b not in parents for b in bnodes):
        return None  # a blank node with no incoming edge — not rooted

    content_cache: dict[Any, str] = {}

    def content_sig(node: Any) -> str:
        cached = content_cache.get(node)
        if cached is not None:
            return cached
        parts = [
            f"{predicate.n3()} {content_sig(obj) if isinstance(obj, rdflib.BNode) else obj.n3()}"
            for predicate, obj in graph.predicate_objects(node)
        ]
        sig = "{" + "|".join(sorted(parts)) + "}"
        content_cache[node] = sig
        return sig

    def path_sig(node: Any) -> str:
        subject, predicate = parents[node]
        base = path_sig(subject) if isinstance(subject, rdflib.BNode) else str(subject.n3())
        return f"{base} {predicate.n3()}"

    # Distinct (path, content) pairs get distinct labels; structurally identical
    # siblings (same path prefix, same content) are disambiguated by a stable
    # index so every blank node ends with a unique N-Triples label.
    keyed: dict[Any, list[Any]] = defaultdict(list)
    for b in bnodes:
        keyed[(path_sig(b), content_sig(b))].append(b)
    labels: dict[Any, Any] = {}
    for i, key in enumerate(sorted(keyed)):
        for j, node in enumerate(keyed[key]):
            labels[node] = rdflib.BNode(f"c{i}x{j}")
    return labels
