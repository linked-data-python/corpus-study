# Context shim (see meta.json): subset of swrl2rdf/prefixmap.py,
# swrl2rdf/model.py and swrl2rdf/builder.py from
# llhhx0826/swrl2rdf@190ffb30687edfef826a50272d0db49038a1086b, so the region
# executes without the package installed. Identical bindings for both
# representations. Trimmed to what the region under study calls: PrefixMap,
# Variable, ClassAtom, SameIndividualAtom, Rule and rules_to_graph (with its
# private helpers), copied verbatim from the source repository.
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import Namespace, OWL, RDF, RDFS, XSD

# --- swrl2rdf/prefixmap.py ---

DEFAULT_PREFIXES: Dict[str, str] = {
    "rdf": str(RDF),
    "rdfs": str(RDFS),
    "owl": str(OWL),
    "xsd": str(XSD),
    "swrl": "http://www.w3.org/2003/11/swrl#",
    "swrla": "http://www.w3.org/2003/11/swrla#",
    "swrlb": "http://www.w3.org/2003/11/swrlb#",
}


class PrefixError(ValueError):
    """Raised when a QName cannot be resolved."""


class PrefixMap:
    """Maps QName prefixes to namespace IRIs."""

    def __init__(self, initial: Optional[Dict[str, str]] = None) -> None:
        self._prefixes: Dict[str, str] = dict(DEFAULT_PREFIXES)
        self._default_prefix: Optional[str] = None
        if initial:
            for k, v in initial.items():
                self.bind(k, v)

    def bind(self, prefix: str, namespace: str) -> None:
        ns = namespace.strip()
        if not ns:
            raise ValueError(f"Empty namespace for prefix '{prefix}'")
        if not (ns.endswith("#") or ns.endswith("/")):
            ns = ns + "#"
        self._prefixes[prefix] = ns

    def items(self):
        return iter(self._prefixes.items())

    def expand(self, qname: str) -> str:
        qname = qname.strip()
        if qname.startswith("<") and qname.endswith(">"):
            return qname[1:-1]
        if qname.startswith("http://") or qname.startswith("https://"):
            return qname
        if ":" not in qname:
            if self._default_prefix:
                return self._prefixes[self._default_prefix] + qname
            raise PrefixError(
                f"Cannot resolve '{qname}': not a QName and not a full IRI. "
                "Use prefix:name, <http://...>, or set --default-prefix."
            )
        prefix, local = qname.split(":", 1)
        if prefix not in self._prefixes:
            raise PrefixError(
                f"Unknown prefix '{prefix}' in '{qname}'. "
                f"Declare it with --prefix {prefix}=<namespace>."
            )
        return self._prefixes[prefix] + local


# --- swrl2rdf/model.py ---

Term = Union["Variable", "LiteralTerm", "IRITerm"]


@dataclass(frozen=True)
class Variable:
    """SWRL variable (?name)."""

    name: str

    def __str__(self) -> str:
        return f"?{self.name}"


@dataclass(frozen=True)
class LiteralTerm:
    value: str
    datatype: Optional[str] = None
    language: Optional[str] = None


@dataclass
class IRITerm:
    full_iri: str
    prefix: Optional[str] = None
    localname: Optional[str] = None


@dataclass
class ClassAtom:
    class_predicate: str
    argument: Term


@dataclass
class SameIndividualAtom:
    arguments: List[Term]


@dataclass
class Rule:
    """A SWRL implication: body atoms -> head atoms."""

    body: List = field(default_factory=list)
    head: List = field(default_factory=list)
    label: Optional[str] = None


# --- swrl2rdf/builder.py ---

SWRL = Namespace("http://www.w3.org/2003/11/swrl#")

SWRL_Imp = SWRL.Imp
SWRL_body = SWRL.body
SWRL_head = SWRL.head
SWRL_AtomList = SWRL.AtomList
SWRL_ClassAtom = SWRL.ClassAtom
SWRL_SameIndividualAtom = SWRL.SameIndividualAtom
SWRL_classPredicate = SWRL.classPredicate
SWRL_argument1 = SWRL.argument1
SWRL_arguments = SWRL.arguments
SWRL_Variable = SWRL.Variable


def rules_to_graph(
    rules: List[Rule],
    prefix_map: PrefixMap,
    graph: Optional[Graph] = None,
) -> Graph:
    """Add SWRL rules to an RDF graph. Never removes existing triples."""
    g = graph if graph is not None else Graph()
    _bind_prefixes(g, prefix_map)
    for rule in rules:
        _add_rule(g, rule, prefix_map)
    return g


def _bind_prefixes(graph: Graph, prefix_map: PrefixMap) -> None:
    for prefix, ns in prefix_map.items():
        graph.bind(prefix, ns, override=False)


def _predicate_ref(name: str, prefix_map: PrefixMap) -> URIRef:
    if name.startswith("http://") or name.startswith("https://"):
        return URIRef(name)
    return URIRef(prefix_map.expand(name))


def _add_rule(graph: Graph, rule: Rule, prefix_map: PrefixMap) -> None:
    imp = BNode()
    graph.add((imp, RDF.type, SWRL_Imp))
    if rule.label:
        graph.add((imp, RDFS.label, Literal(rule.label)))
    body_list = _build_atom_list(graph, rule.body, prefix_map)
    head_list = _build_atom_list(graph, rule.head, prefix_map)
    graph.add((imp, SWRL_body, body_list))
    graph.add((imp, SWRL_head, head_list))


def _build_atom_list(graph: Graph, atoms: List, prefix_map: PrefixMap) -> BNode:
    list_head = BNode()
    current = list_head
    for i, atom in enumerate(atoms):
        atom_node = _build_atom(graph, atom, prefix_map)
        graph.add((current, RDF.type, SWRL_AtomList))
        graph.add((current, RDF.first, atom_node))
        if i < len(atoms) - 1:
            rest = BNode()
            graph.add((current, RDF.rest, rest))
            current = rest
        else:
            graph.add((current, RDF.rest, RDF.nil))
    if not atoms:
        graph.add((list_head, RDF.type, SWRL_AtomList))
        graph.add((list_head, RDF.first, RDF.nil))
        graph.add((list_head, RDF.rest, RDF.nil))
    return list_head


def _build_atom(graph: Graph, atom, prefix_map: PrefixMap) -> BNode:
    node = BNode()
    var_map: Dict[str, BNode] = {}

    if isinstance(atom, ClassAtom):
        graph.add((node, RDF.type, SWRL_ClassAtom))
        graph.add(
            (node, SWRL_classPredicate, _predicate_ref(atom.class_predicate, prefix_map))
        )
        graph.add(
            (node, SWRL_argument1, _term_node(graph, atom.argument, prefix_map, var_map))
        )

    elif isinstance(atom, SameIndividualAtom):
        graph.add((node, RDF.type, SWRL_SameIndividualAtom))
        _add_multi_arguments(graph, node, atom.arguments, prefix_map, var_map)

    return node


def _add_multi_arguments(
    graph: Graph,
    node: BNode,
    arguments: List,
    prefix_map: PrefixMap,
    var_map: Dict[str, BNode],
) -> None:
    arg_nodes = [_term_node(graph, t, prefix_map, var_map) for t in arguments]
    args_bnode = BNode()
    Collection(graph, args_bnode, arg_nodes)
    graph.add((node, SWRL_arguments, args_bnode))


def _term_node(
    graph: Graph,
    term,
    prefix_map: PrefixMap,
    var_map: Dict[str, BNode],
):
    if isinstance(term, Variable):
        if term.name not in var_map:
            v = BNode()
            graph.add((v, RDF.type, SWRL_Variable))
            var_map[term.name] = v
        return var_map[term.name]
    if isinstance(term, LiteralTerm):
        if term.datatype:
            dt = term.datatype
            if not dt.startswith("http"):
                dt = prefix_map.expand(term.datatype) if ":" in term.datatype else dt
            return Literal(term.value, datatype=URIRef(dt))
        if term.language:
            return Literal(term.value, lang=term.language)
        return Literal(term.value)
    if isinstance(term, IRITerm):
        return URIRef(term.full_iri)
    raise TypeError(f"Unknown term type: {type(term)}")
