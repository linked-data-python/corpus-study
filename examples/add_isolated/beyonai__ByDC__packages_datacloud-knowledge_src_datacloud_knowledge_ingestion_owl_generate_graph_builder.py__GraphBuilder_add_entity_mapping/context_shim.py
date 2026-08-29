# Context shim (see meta.json): stand-ins for what surrounds
# GraphBuilder.add_entity_mapping in
# beyonai/ByDC@8c0643fb26213a2f1e39582c594f561cede9ee67 :
# packages/datacloud-knowledge/src/datacloud_knowledge/ingestion/owl_generate/graph_builder.py
# so the region executes standalone -- the extracted region has NO imports
# at all (163-region case per AGENT_BATCH.md: `self._graph`, `self._RDF`,
# `self._ns` and the module-level `_safe_xml_id` are all bindings the
# sampled context lines dropped). Identical bindings for both
# representations.
#
# _safe_xml_id, _DEFAULT_BASE, GraphBuilderStub.__init__ and ._add_literal
# are transcribed VERBATIM from the local clone
# (corpus/repos/beyonai__ByDC/packages/datacloud-knowledge/src/datacloud_knowledge/ingestion/owl_generate/graph_builder.py,
# lines 97-99, 55, 143-166, 693-698). GraphBuilderStub carries only what
# add_entity_mapping's own body reads on `self`.
import re

_DEFAULT_BASE = "http://example.org/entity/ontology#"


def _safe_xml_id(value: str, max_len: int = 200) -> str:
    """将字符串转为合法 XML NCName 片段。"""
    return re.sub(r"[^\w]", "_", value)[:max_len]


class GraphBuilderStub:
    def __init__(self, base: str = _DEFAULT_BASE) -> None:
        from rdflib import OWL, RDF, RDFS, XSD, Graph, Namespace

        self._graph = Graph()
        self._base = base
        self._RDF = RDF
        self._RDFS = RDFS
        self._OWL = OWL
        self._XSD = XSD

        self._ns = Namespace(base)

        self._graph.bind("", self._ns)
        self._graph.bind("owl", OWL)
        self._graph.bind("rdf", RDF)
        self._graph.bind("rdfs", RDFS)
        self._graph.bind("xsd", XSD)

    def _add_literal(self, subject, predicate, value: str) -> None:
        """添加字面值三元组 (s, p, "value"^^xsd:string)。"""
        from rdflib import Literal

        self._graph.add((subject, predicate, Literal(value, datatype=self._XSD.string)))
