# Extracted from RDFLib/pySHACL@469cca7a22 : pyshacl/rdfutil/stringify.py
# region: stringify_blank_node (lines 28-94, stratum ns_import_project)
# licence of the source repository: see meta.json
from typing import Iterator, List, Optional, Tuple, Union, cast
import rdflib
from rdflib.namespace import NamespaceManager
from .consts import OWL, SH, RDF_first, RDFNode
OWLsameAs = OWL.sameAs

@with_dict_cache
def stringify_blank_node(
    graph: rdflib.Graph, bnode: rdflib.BNode, ns_manager: Optional[NamespaceManager] = None, recursion: int = 0
):
    if isinstance(graph, rdflib.Dataset):
        raise RuntimeError("Can only stringify a blank node when graph is a rdflib.Graph")
    assert isinstance(graph, rdflib.Graph)
    assert isinstance(bnode, rdflib.BNode)
    if recursion >= 12:
        return "<http://recursion.too.deep>"
    stringed_cache_key = id(graph), str(bnode)

    try:
        cached = stringify_blank_node.dict_cache[stringed_cache_key]
        return cached
    except LookupError:
        pass
    if ns_manager is None:  # pragma: no cover
        ns_manager = graph.namespace_manager
        ns_manager.bind("sh", SH)

    def stringify_list(node: rdflib.BNode) -> str:
        nonlocal graph, ns_manager, recursion
        item_texts: List[str] = []
        for item in iter(graph.items(node)):
            item_text = stringify_node(graph, item, ns_manager=ns_manager, recursion=recursion + 1)
            item_texts.append(item_text)
        # item_texts.sort()  ## Don't sort, to preserve list order
        return "( {} )".format(" ".join(item_texts))

    predicates: List[RDFNode] = list(cast(Iterator[RDFNode], graph.predicates(bnode)))
    if len(predicates) < 1:
        return "[ ]"
    if RDF_first in predicates:
        return stringify_list(bnode)
    p_string_map = {}
    for p in predicates:
        if isinstance(p, (rdflib.Literal, rdflib.BNode, rdflib.URIRef)):
            p_string = p.n3(namespace_manager=ns_manager)
        else:
            p_string = str(p)
        objs: List[RDFNode] = list(cast(Iterator[RDFNode], graph.objects(bnode, p)))
        if len(objs) < 1:
            continue
        o_texts = []
        for o in objs:
            if p is OWLsameAs and o is bnode:
                # Avoid a crazy owl:sameAs recursion with self.
                o_texts.append("<self>")
            else:
                o_text = stringify_node(graph, o, ns_manager=ns_manager, recursion=recursion + 1)
                o_texts.append(o_text)
        if len(o_texts) > 1:
            o_texts.sort()
            o_text = ", ".join(o_texts)
        else:
            o_text = o_texts[0]
        p_string_map[p_string] = o_text
    if len(p_string_map) > 1:
        g = ["{} {}".format(p, o) for p, o in sorted(p_string_map.items())]
        blank_string = " ; ".join(g)
    else:
        _p, _o = next(iter(p_string_map.items()))
        blank_string = "{} {}".format(_p, _o)
    blank_string = "[ {} ]".format(blank_string)
    stringify_blank_node.dict_cache[stringed_cache_key] = blank_string
    return blank_string
