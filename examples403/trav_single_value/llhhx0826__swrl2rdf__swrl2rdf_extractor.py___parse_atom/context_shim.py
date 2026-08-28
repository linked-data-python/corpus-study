# Context shim (see meta.json): the SWRL namespace constant and the sibling
# helpers _parse_atom calls, transcribed from
# llhhx0826/swrl2rdf@190ffb30687edfef826a50272d0db49038a1086b so the region
# executes outside the package -- swrl2rdf is a GitHub project, not on PyPI,
# and is not in the study venv (pinned to rdflib 7.2.1 only).
# Identical bindings for both representations.
#
# SWRL: swrl2rdf/extractor.py, module level, just above the SWRL_* = SWRL.xxx
# assignments that the pipeline's context lines DID capture (those stayed in
# original.py / translated.ldpy) -- the pipeline's line window missed the
# `SWRL = Namespace(...)` line itself.
#
# _is_variable, _display_iri, _term_from_node, _terms_from_arguments:
# swrl2rdf/extractor.py siblings of _parse_atom, called by it, verbatim.
#
# Variable, LiteralTerm, IRITerm, ClassAtom, IndividualPropertyAtom,
# DatavaluedPropertyAtom, BuiltinAtom, SameIndividualAtom,
# DifferentIndividualsAtom, Atom, Term: swrl2rdf/model.py, verbatim.
#
# PrefixMap, DEFAULT_PREFIXES: swrl2rdf/prefixmap.py, verbatim except
# `expand()` and `set_default_prefix()`, which _parse_atom's call graph never
# reaches (only `.compact()` and `.default_prefix` are read) and are left out
# rather than transcribed unexercised.
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import Namespace, OWL, RDF, RDFS, XSD

SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
SWRL_arguments = SWRL.arguments
SWRL_argument1 = SWRL.argument1
SWRL_argument2 = SWRL.argument2
SWRL_Variable = SWRL.Variable


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
    """RDF literal value in a rule."""

    value: str
    datatype: Optional[str] = None
    language: Optional[str] = None

    def __str__(self) -> str:
        if self.language:
            return f'"{self.value}"@{self.language}'
        if self.datatype:
            return f'"{self.value}"^^{self.datatype}'
        return f'"{self.value}"'


@dataclass
class IRITerm:
    """Named class, property, individual, or builtin IRI."""

    full_iri: str
    prefix: Optional[str] = None
    localname: Optional[str] = None

    @property
    def qname(self) -> str:
        if self.prefix is not None and self.localname is not None:
            return f"{self.prefix}:{self.localname}"
        return self.full_iri

    def __str__(self) -> str:
        if self.prefix is not None and self.localname is not None:
            return f"{self.prefix}:{self.localname}"
        if self.full_iri.startswith("http"):
            return f"<{self.full_iri}>"
        return self.full_iri


@dataclass
class ClassAtom:
    class_predicate: str
    argument: Term


@dataclass
class IndividualPropertyAtom:
    property_predicate: str
    argument1: Term
    argument2: Term


@dataclass
class DatavaluedPropertyAtom:
    property_predicate: str
    argument1: Term
    argument2: Term


@dataclass
class BuiltinAtom:
    builtin: str
    arguments: List[Term]


@dataclass
class SameIndividualAtom:
    arguments: List[Term]


@dataclass
class DifferentIndividualsAtom:
    arguments: List[Term]


Atom = Union[
    ClassAtom,
    IndividualPropertyAtom,
    DatavaluedPropertyAtom,
    BuiltinAtom,
    SameIndividualAtom,
    DifferentIndividualsAtom,
]


@dataclass
class Rule:
    """A SWRL implication: body atoms -> head atoms. (unused by this region;
    kept so `from swrl2rdf.model import (..., Rule, ...)` has something to
    bind, exactly as the real module would provide.)"""

    body: List[Atom]
    head: List[Atom]
    label: Optional[str] = None


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

    @property
    def default_prefix(self) -> Optional[str]:
        return self._default_prefix

    def compact(self, iri: str, preferred_prefixes=None) -> str:
        """Compact an IRI to QName if possible."""
        if preferred_prefixes:
            order = list(preferred_prefixes)
        elif self._default_prefix:
            order = [self._default_prefix] + sorted(
                (p for p in self._prefixes if p != self._default_prefix),
                key=lambda p: -len(self._prefixes[p]),
            )
        else:
            order = sorted(self._prefixes.keys(), key=lambda p: -len(self._prefixes[p]))
        for prefix in order:
            if prefix not in self._prefixes:
                continue
            ns = self._prefixes[prefix]
            if iri.startswith(ns):
                local = iri[len(ns):]
                if prefix == self._default_prefix:
                    return local
                return f"{prefix}:{local}"
        return f"<{iri}>"

    @classmethod
    def from_graph(cls, graph: Graph) -> "PrefixMap":
        pm = cls()
        for prefix, namespace in graph.namespace_manager.namespaces():
            pm._prefixes[str(prefix)] = str(namespace)
        return pm


# --- swrl2rdf/extractor.py siblings of _parse_atom ---

def _is_variable(graph: Graph, node) -> bool:
    return (node, RDF.type, SWRL_Variable) in graph


def _display_iri(node, prefix_map: "PrefixMap", reverse_mapping: Optional[Dict[str, str]]) -> str:
    if node is None:
        return ""
    if not isinstance(node, URIRef):
        return str(node)
    iri = str(node)
    if reverse_mapping and iri in reverse_mapping:
        return reverse_mapping[iri]
    compact = prefix_map.compact(iri)
    if (
        prefix_map.default_prefix
        and ":" not in compact
        and not compact.startswith("<")
    ):
        return compact
    if compact.startswith(":"):
        return compact[1:]
    return compact


def _term_from_node(graph, node, prefix_map, var_names, reverse_mapping):
    if node is None:
        raise ValueError("Missing argument in SWRL atom")
    if isinstance(node, Literal):
        if node.language:
            return LiteralTerm(value=str(node), language=node.language)
        if node.datatype:
            dt = prefix_map.compact(str(node.datatype))
            return LiteralTerm(value=str(node), datatype=dt)
        return LiteralTerm(value=str(node))
    if _is_variable(graph, node):
        name = var_names.get(node)
        if not name and isinstance(node, URIRef) and node.fragment:
            name = node.fragment.lstrip("?")
        if not name:
            name = "var1"
        return Variable(name=name)
    if isinstance(node, URIRef):
        iri = str(node)
        if reverse_mapping and iri in reverse_mapping:
            qname = reverse_mapping[iri]
            if ":" in qname:
                p, local = qname.split(":", 1)
                return IRITerm(full_iri=iri, prefix=p, localname=local)
        compact = prefix_map.compact(iri)
        if ":" in compact and not compact.startswith("<"):
            p, local = compact.split(":", 1)
            return IRITerm(full_iri=iri, prefix=p, localname=local)
        if prefix_map.default_prefix and not compact.startswith("<"):
            return IRITerm(
                full_iri=iri,
                prefix=prefix_map.default_prefix,
                localname=compact,
            )
        return IRITerm(full_iri=iri)
    if isinstance(node, BNode):
        if node in var_names:
            return Variable(name=var_names[node])
        return Variable(name="var1")
    raise ValueError(f"Unsupported term node: {node}")


def _terms_from_arguments(graph, atom_node, prefix_map, var_names, reverse_mapping):
    from rdflib.collection import Collection
    args_node = graph.value(atom_node, SWRL_arguments)
    if args_node is None:
        a1 = graph.value(atom_node, SWRL_argument1)
        a2 = graph.value(atom_node, SWRL_argument2)
        terms: List[Term] = []
        if a1 is not None:
            terms.append(_term_from_node(graph, a1, prefix_map, var_names, reverse_mapping))
        if a2 is not None:
            terms.append(_term_from_node(graph, a2, prefix_map, var_names, reverse_mapping))
        return terms
    try:
        coll = Collection(graph, args_node)
        return [
            _term_from_node(graph, item, prefix_map, var_names, reverse_mapping)
            for item in coll
        ]
    except Exception:
        return []
