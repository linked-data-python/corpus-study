"""AST-based RDF-usage analysis of Python source files.

The analyser distinguishes *actual* RDF operations from incidental
occurrences (an imported name never used, a ``.add`` on a set, a local
variable that happens to be called ``Literal``) by tracking, flow-insensitively
but scope-aware at module level:

  * which local names are bound to rdflib entities by imports
    (``from rdflib import Graph as G`` binds ``G`` -> ``rdflib.Graph``);
  * which variables are bound to *namespace objects* — well-known namespaces
    imported from ``rdflib.namespace`` (``RDF``, ``FOAF``…), results of
    ``Namespace(...)`` / ``ClosedNamespace(...)`` calls, and subclasses of
    ``DefinedNamespace``;
  * which variables are bound to *graph objects* — results of ``Graph()``,
    ``ConjunctiveGraph()``, ``Dataset()`` and of graph-returning methods.

Every RDF operation found is recorded as an :class:`RdfOp` with its category,
location, and the size of its AST subtree.  Subtree nodes are marked so that
nested operations are not double counted at the *node census* level
(``rdf_ast_nodes``), while each operation still counts once in its own
category (a ``URIRef(...)`` inside ``g.add(...)`` is one term construction
*and* contributes its nodes to the enclosing add's subtree only once).

Metric definitions
------------------

total_loc          physical lines in the file
code_loc           lines holding at least one code token (tokenize-based;
                   excludes blank lines and comment-only lines)
logical_loc        number of ``ast.stmt`` nodes (statement count)
tokens             number of significant tokens (NAME/OP/NUMBER/STRING,
                   f-string parts; excludes COMMENT/NL/NEWLINE/INDENT/DEDENT
                   and the encoding/endmarker pseudo-tokens)
ast_nodes          total number of AST nodes in the module
rdf_ast_nodes      number of AST nodes belonging to at least one detected
                   RDF operation's subtree (each node counted once)
rdf_node_density   rdf_ast_nodes / ast_nodes  (0 if ast_nodes == 0)
rdf_line_density   lines containing at least one RDF operation / code_loc
rdf_ops            total number of detected RDF operations
terms_constructed  operations in categories term_constructor + namespace_term
constructors       explicit rdflib constructor calls (URIRef/Literal/BNode/
                   Namespace/Graph/…)
triples_added      number of ``.add((s,p,o))`` / ``.set`` calls with an
                   explicit 3-tuple (each is exactly one triple)
quads_added        same for 4-tuples on Dataset/ConjunctiveGraph
graph_ops          graph-level operations (add/remove/triples/…/parse/
                   serialize/query/update/bind)

Operation categories (RdfOp.category):

  term_constructor   URIRef(...), Literal(...), BNode(...), Variable(...)
  namespace_ctor     Namespace(...), ClosedNamespace(...), NamespaceManager(...),
                     DefinedNamespace subclass definition
  namespace_term     NS.term / NS["term"] on a known namespace object
  graph_ctor         Graph(), ConjunctiveGraph(), Dataset()
  triple_add         g.add((s,p,o)) with explicit tuple / g.set((s,p,o))
  quad_add           g.add((s,p,o,c)) with explicit 4-tuple
  bulk_add           g.addN(...) / g += / g.add(t) with non-literal tuple
  graph_read         triples/quads/subjects/objects/predicates/value/items/
                     subject_objects/…/__contains__/iteration constructs
  graph_write        remove/remove_context/bind/add_graph/destroy…
  serialize_parse    g.parse(...), g.serialize(...), plugin registration
  sparql             g.query/g.update/prepareQuery/prepareUpdate/processUpdate
"""

from __future__ import annotations

import ast
import io
import tokenize
from dataclasses import dataclass, field

# --- rdflib surface --------------------------------------------------------

RDFLIB_MODULES = {
    "rdflib", "rdflib.namespace", "rdflib.term", "rdflib.graph",
    "rdflib.plugins.sparql", "rdflib.plugins.sparql.processor",
    "rdflib.collection", "rdflib.compare", "rdflib.util", "rdflib.plugin",
}

TERM_CONSTRUCTORS = {"URIRef", "Literal", "BNode", "Variable"}
NAMESPACE_CONSTRUCTORS = {"Namespace", "ClosedNamespace", "NamespaceManager"}
GRAPH_CONSTRUCTORS = {"Graph", "ConjunctiveGraph", "Dataset", "QuotedGraph"}
SPARQL_FUNCTIONS = {"prepareQuery", "prepareUpdate", "processUpdate"}
COLLECTION_CONSTRUCTORS = {"Collection"}

# Well-known namespace objects exported by rdflib.namespace (static list for
# reproducibility across rdflib versions; extras are harmless).
WELL_KNOWN_NAMESPACES = {
    "RDF", "RDFS", "OWL", "XSD", "FOAF", "SKOS", "DC", "DCTERMS", "DCAT",
    "DCMITYPE", "DOAP", "VOID", "XMLNS", "BRICK", "CSVW", "GEO", "ODRL2",
    "ORG", "PROF", "PROV", "QB", "SDO", "SH", "SOSA", "SSN", "TIME", "VANN",
    "WGS",
}

GRAPH_READ_METHODS = {
    "triples", "quads", "subjects", "objects", "predicates",
    "subject_objects", "subject_predicates", "predicate_objects",
    "value", "items", "transitive_objects", "transitive_subjects",
    "triples_choices", "label", "preferredLabel", "compute_qname",
    "qname", "n3", "contexts", "get_context", "graphs",
}
GRAPH_WRITE_METHODS = {
    "remove", "set", "remove_context", "remove_graph", "add_graph",
    "destroy", "commit", "rollback", "open", "close", "bind",
}
GRAPH_IO_METHODS = {"parse", "serialize", "load"}
GRAPH_SPARQL_METHODS = {"query", "update"}
GRAPH_RETURNING_METHODS = {"get_context", "graph", "skolemize", "de_skolemize"}


@dataclass
class RdfOp:
    """One detected RDF operation."""
    category: str
    detail: str          # e.g. "URIRef", "add", "FOAF.name"
    lineno: int
    end_lineno: int
    col: int
    subtree_nodes: int   # size of the operation's AST subtree
    certain: bool        # False for pattern-matched ops on unknown receivers

    def to_dict(self) -> dict:
        return {
            "category": self.category, "detail": self.detail,
            "lineno": self.lineno, "end_lineno": self.end_lineno,
            "subtree_nodes": self.subtree_nodes, "certain": self.certain,
        }


@dataclass
class FileAnalysis:
    path: str
    total_loc: int = 0
    code_loc: int = 0
    logical_loc: int = 0
    tokens: int = 0
    ast_nodes: int = 0
    rdf_ast_nodes: int = 0
    rdf_lines: int = 0
    imports_rdflib: bool = False
    ops: list[RdfOp] = field(default_factory=list)
    category_counts: dict[str, int] = field(default_factory=dict)
    error: str | None = None

    # --- derived -----------------------------------------------------------
    @property
    def rdf_ops(self) -> int:
        return len(self.ops)

    @property
    def certain_ops(self) -> int:
        return sum(1 for o in self.ops if o.certain)

    @property
    def rdf_node_density(self) -> float:
        return self.rdf_ast_nodes / self.ast_nodes if self.ast_nodes else 0.0

    @property
    def rdf_line_density(self) -> float:
        return self.rdf_lines / self.code_loc if self.code_loc else 0.0

    @property
    def terms_constructed(self) -> int:
        c = self.category_counts
        return c.get("term_constructor", 0) + c.get("namespace_term", 0)

    @property
    def constructors(self) -> int:
        c = self.category_counts
        return (c.get("term_constructor", 0) + c.get("namespace_ctor", 0)
                + c.get("graph_ctor", 0))

    @property
    def triples_added(self) -> int:
        return self.category_counts.get("triple_add", 0)

    @property
    def quads_added(self) -> int:
        return self.category_counts.get("quad_add", 0)

    @property
    def graph_ops(self) -> int:
        c = self.category_counts
        return sum(c.get(k, 0) for k in (
            "triple_add", "quad_add", "bulk_add", "graph_read",
            "graph_write", "serialize_parse", "sparql", "graph_ctor"))

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "total_loc": self.total_loc, "code_loc": self.code_loc,
            "logical_loc": self.logical_loc, "tokens": self.tokens,
            "ast_nodes": self.ast_nodes, "rdf_ast_nodes": self.rdf_ast_nodes,
            "rdf_lines": self.rdf_lines,
            "imports_rdflib": self.imports_rdflib,
            "rdf_ops": self.rdf_ops, "certain_ops": self.certain_ops,
            "rdf_node_density": round(self.rdf_node_density, 6),
            "rdf_line_density": round(self.rdf_line_density, 6),
            "terms_constructed": self.terms_constructed,
            "constructors": self.constructors,
            "triples_added": self.triples_added,
            "quads_added": self.quads_added,
            "graph_ops": self.graph_ops,
            "category_counts": dict(sorted(self.category_counts.items())),
            "error": self.error,
        }


SIGNIFICANT_TOKENS = {
    tokenize.NAME, tokenize.OP, tokenize.NUMBER, tokenize.STRING,
} | {
    t for t in (getattr(tokenize, n, None) for n in
                ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"))
    if t is not None
}


def _surface_metrics(source: str, analysis: FileAnalysis) -> None:
    lines = source.splitlines()
    analysis.total_loc = len(lines)
    code_lines: set[int] = set()
    ntok = 0
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type in SIGNIFICANT_TOKENS and tok.string.strip():
                ntok += 1
                for ln in range(tok.start[0], tok.end[0] + 1):
                    code_lines.add(ln)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    analysis.tokens = ntok
    analysis.code_loc = len(code_lines)


class _Bindings:
    """Names bound to rdflib entities, namespace objects and graph objects."""

    def __init__(self) -> None:
        # local name -> rdflib qualified name, e.g. {"G": "Graph"}
        self.rdflib_names: dict[str, str] = {}
        # local module aliases, e.g. {"rdflib": "rdflib", "rl": "rdflib"}
        self.module_aliases: dict[str, str] = {}
        self.namespace_vars: set[str] = set()
        self.graph_vars: set[str] = set()

    def rdflib_callee(self, node: ast.expr) -> str | None:
        """Return the rdflib entity name a call target resolves to, or None."""
        if isinstance(node, ast.Name):
            return self.rdflib_names.get(node.id)
        if isinstance(node, ast.Attribute):
            base = node.value
            if isinstance(base, ast.Name) and base.id in self.module_aliases:
                return node.attr
            if isinstance(base, ast.Attribute):  # rdflib.namespace.Namespace
                root = base
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name) and root.id in self.module_aliases:
                    return node.attr
        return None


def _iter_positioned(node: ast.AST):
    """All nodes of the subtree that carry a source position.

    The AST-node census is defined over *positioned* nodes only (statements,
    expressions, keywords, aliases).  Context markers (Load/Store/Del) and
    operator tokens are shared singleton instances in CPython, which would
    corrupt identity-based bookkeeping, and they carry no source information.
    """
    for sub in ast.walk(node):
        if hasattr(sub, "lineno"):
            yield sub


def _count_nodes(node: ast.AST) -> int:
    return sum(1 for _ in _iter_positioned(node))


class _Analyzer(ast.NodeVisitor):
    def __init__(self, analysis: FileAnalysis) -> None:
        self.a = analysis
        self.b = _Bindings()
        self.marked: set[int] = set()   # ids of nodes already in an RDF subtree

    # --- imports -----------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "rdflib" or alias.name.startswith("rdflib."):
                self.a.imports_rdflib = True
                self.b.module_aliases[alias.asname or alias.name.split(".")[0]] = "rdflib"
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        if mod == "rdflib" or mod.startswith("rdflib."):
            self.a.imports_rdflib = True
            for alias in node.names:
                local = alias.asname or alias.name
                self.b.rdflib_names[local] = alias.name
                if alias.name in WELL_KNOWN_NAMESPACES:
                    self.b.namespace_vars.add(local)
        self.generic_visit(node)

    # --- assignments: propagate namespace/graph-ness ------------------------

    def _targets(self, node: ast.AST) -> list[str]:
        names: list[str] = []
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name):
                names.append(t.id)
            elif isinstance(t, ast.Attribute):
                names.append(t.attr)  # self.g = Graph() -> track "g" loosely
        return names

    def _classify_value(self, value: ast.expr) -> str | None:
        """'namespace' | 'graph' | None for the value expression."""
        if isinstance(value, ast.Call):
            callee = self.b.rdflib_callee(value.func)
            if callee in NAMESPACE_CONSTRUCTORS and callee != "NamespaceManager":
                return "namespace"
            if callee in GRAPH_CONSTRUCTORS:
                return "graph"
            if (isinstance(value.func, ast.Attribute)
                    and value.func.attr in GRAPH_RETURNING_METHODS
                    and self._is_graph(value.func.value)):
                return "graph"
            # g = rdflib.Graph().parse(...) chains: parse/load return the graph
            if (isinstance(value.func, ast.Attribute)
                    and value.func.attr in GRAPH_IO_METHODS
                    and self._classify_value_expr_is_graph(value.func.value)):
                return "graph"
        return None

    def _classify_value_expr_is_graph(self, expr: ast.expr) -> bool:
        if self._is_graph(expr):
            return True
        if isinstance(expr, ast.Call):
            callee = self.b.rdflib_callee(expr.func)
            return callee in GRAPH_CONSTRUCTORS
        return False

    def visit_Assign(self, node: ast.Assign) -> None:
        kind = self._classify_value(node.value)
        if kind == "namespace":
            self.b.namespace_vars.update(self._targets(node))
        elif kind == "graph":
            self.b.graph_vars.update(self._targets(node))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            kind = self._classify_value(node.value)
            if kind == "namespace":
                self.b.namespace_vars.update(self._targets(node))
            elif kind == "graph":
                self.b.graph_vars.update(self._targets(node))
        self.generic_visit(node)

    # --- DefinedNamespace subclasses ----------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for base in node.bases:
            name = self.b.rdflib_callee(base) or (
                base.id if isinstance(base, ast.Name) else None)
            if name == "DefinedNamespace":
                self.b.namespace_vars.add(node.name)
                self._record("namespace_ctor", f"class {node.name}", node,
                             certain=True, mark_subtree=False)
        self.generic_visit(node)

    # --- receivers ----------------------------------------------------------

    def _is_graph(self, expr: ast.expr) -> bool:
        if isinstance(expr, ast.Name):
            return expr.id in self.b.graph_vars
        if isinstance(expr, ast.Attribute):     # self.graph, obj.g
            return expr.attr in self.b.graph_vars
        return False

    def _is_namespace(self, expr: ast.expr) -> bool:
        if isinstance(expr, ast.Name):
            return expr.id in self.b.namespace_vars
        if isinstance(expr, ast.Attribute):
            return expr.attr in self.b.namespace_vars
        return False

    def _is_rdf_term_expr(self, expr: ast.expr) -> bool:
        """Heuristic: does this expression construct/denote an RDF term?"""
        if isinstance(expr, ast.Call):
            callee = self.b.rdflib_callee(expr.func)
            return callee in TERM_CONSTRUCTORS
        if isinstance(expr, ast.Attribute):
            return self._is_namespace(expr.value)
        if isinstance(expr, ast.Subscript):
            return self._is_namespace(expr.value)
        if isinstance(expr, ast.Name):
            return expr.id in self.b.namespace_vars
        return False

    # --- recording ----------------------------------------------------------

    def _record(self, category: str, detail: str, node: ast.AST, *,
                certain: bool, mark_subtree: bool = True) -> None:
        size = _count_nodes(node)
        self.a.ops.append(RdfOp(
            category=category, detail=detail,
            lineno=getattr(node, "lineno", 0),
            end_lineno=getattr(node, "end_lineno", 0) or getattr(node, "lineno", 0),
            col=getattr(node, "col_offset", 0),
            subtree_nodes=size, certain=certain))
        self.a.category_counts[category] = self.a.category_counts.get(category, 0) + 1
        if mark_subtree:
            for sub in _iter_positioned(node):
                self.marked.add(id(sub))

    # --- calls --------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        callee = self.b.rdflib_callee(node.func)
        if callee in TERM_CONSTRUCTORS:
            self._record("term_constructor", callee, node, certain=True)
        elif callee in NAMESPACE_CONSTRUCTORS:
            self._record("namespace_ctor", callee, node, certain=True)
        elif callee in GRAPH_CONSTRUCTORS:
            self._record("graph_ctor", callee, node, certain=True)
        elif callee in SPARQL_FUNCTIONS:
            self._record("sparql", callee, node, certain=True)
        elif callee in COLLECTION_CONSTRUCTORS:
            self._record("graph_write", callee, node, certain=True)
        elif isinstance(node.func, ast.Attribute):
            self._method_call(node, node.func)
        self.generic_visit(node)

    def _method_call(self, node: ast.Call, func: ast.Attribute) -> None:
        method = func.attr
        recv_graph = self._is_graph(func.value)
        # ---- add/set: triple or quad ---------------------------------------
        if method in ("add", "set"):
            arg = node.args[0] if node.args else None
            if isinstance(arg, ast.Tuple) and len(arg.elts) in (3, 4):
                looks_rdf = any(self._is_rdf_term_expr(e) for e in arg.elts)
                if recv_graph or looks_rdf:
                    cat = "triple_add" if len(arg.elts) == 3 else "quad_add"
                    self._record(cat, method, node,
                                 certain=recv_graph or looks_rdf)
            elif recv_graph and arg is not None:
                self._record("bulk_add", method, node, certain=True)
            return
        if method == "addN":
            args_rdf = any(self._is_rdf_term_expr(a) for a in node.args)
            if recv_graph or args_rdf:
                self._record("bulk_add", method, node, certain=recv_graph)
            return
        # ---- other graph methods: only on known graph receivers ------------
        if recv_graph:
            if method in GRAPH_READ_METHODS:
                self._record("graph_read", method, node, certain=True)
            elif method in GRAPH_WRITE_METHODS:
                self._record("graph_write", method, node, certain=True)
            elif method in GRAPH_IO_METHODS:
                self._record("serialize_parse", method, node, certain=True)
            elif method in GRAPH_SPARQL_METHODS:
                self._record("sparql", method, node, certain=True)
            return
        # ---- pattern-matched, uncertain receivers ---------------------------
        if method in ("triples", "quads") and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Tuple) and len(arg.elts) in (3, 4):
                if any(self._is_rdf_term_expr(e) for e in arg.elts) or any(
                        isinstance(e, ast.Constant) and e.value is None
                        for e in arg.elts):
                    self._record("graph_read", method, node, certain=False)
        elif method == "remove" and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Tuple) and len(arg.elts) == 3 and any(
                    self._is_rdf_term_expr(e) or
                    (isinstance(e, ast.Constant) and e.value is None)
                    for e in arg.elts):
                self._record("graph_write", method, node, certain=False)

    # --- namespace-derived terms -------------------------------------------

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._is_namespace(node.value):
            self._record("namespace_term",
                         f"{ast.unparse(node.value)}.{node.attr}",
                         node, certain=True)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if self._is_namespace(node.value):
            self._record("namespace_term", ast.unparse(node.value) + "[…]",
                         node, certain=True)
        self.generic_visit(node)


def analyze_source(source: str, path: str = "<string>") -> FileAnalysis:
    """Analyse one Python source text."""
    a = FileAnalysis(path=path)
    _surface_metrics(source, a)
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, MemoryError, RecursionError) as e:
        a.error = f"{type(e).__name__}: {e}"
        return a
    a.ast_nodes = _count_nodes(tree)
    a.logical_loc = sum(isinstance(n, ast.stmt) for n in ast.walk(tree))
    # Two passes: the analysis is flow-insensitive, so a first pass collects
    # every binding (imports, NS = Namespace(...), g = Graph()), and a second
    # pass — with those bindings pre-seeded — records the operations.  This
    # catches uses that lexically precede the binding site.
    first = _Analyzer(a)
    first.visit(tree)
    a.ops, a.category_counts = [], {}
    visitor = _Analyzer(a)
    visitor.b = first.b
    visitor.visit(tree)
    a.rdf_ast_nodes = len(visitor.marked)
    lines: set[int] = set()
    for op in a.ops:
        lines.update(range(op.lineno, op.end_lineno + 1))
    a.rdf_lines = len(lines)
    return a


def analyze_file(path) -> FileAnalysis:
    try:
        source = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        a = FileAnalysis(path=str(path))
        a.error = f"OSError: {e}"
        return a
    return analyze_source(source, str(path))
