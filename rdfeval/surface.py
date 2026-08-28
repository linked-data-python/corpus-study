"""Design-oriented surface analysis: which *shapes* does real RDFLib code take?

Where :mod:`rdfeval.analyze` measures *how much* RDF a file contains, this
module measures *what kind of thing* that RDF code does, in the exact shapes a
language designer needs in order to decide which notation extensions would pay
off.  Every family of counters below answers one open proposal (ROADMAP §A):

  Q1 ``ns_*``      namespace definition, sharing and reuse
                   -> is ``export @prefix`` / ``import ex:`` worth a language
                      construct, or does ``Namespace(...)`` already suffice?
  Q2 ``sparql_*``  query/update calls, how the query text is built and consumed
                   -> what would first-class SPARQL have to cover?
  Q3 ``trav_*``    triple selection and graph traversal, and their syntactic
                   context (loop, comprehension, ``next``, chaining)
                   -> is a traversal notation warranted, and of which shape?
  Q4 ``bind_*``    binding of terms into queries (``initBindings``, string
                   interpolation of terms)
                   -> what would ``g @ {?v: term}`` actually replace?
  Q5 ``add_*``     ``Graph.add`` shapes: runs of consecutive adds, shared
                   subjects, loops, receiver length, constant vs computed terms
                   -> how much does one ``g += g{...}`` island amortise?
  Q6 ``graph_*``   how many graphs are in play, and are they named?
                   -> does a "current graph" declaration have a referent?

The analysis is deliberately *surface*: it counts syntactic shapes, never
semantics.  A shape is only counted when the receiver is a known graph or
namespace object, using the same flow-insensitive, two-pass name resolution as
:mod:`rdfeval.analyze` (imports, ``NS = Namespace(...)``, ``g = Graph()``,
annotations); the one exception is :func:`_query_shape`, which reads a literal
query string to classify its form.

Outputs::

    results/raw/surface.jsonl        one JSON object per RDF-relevant file
    results/summary/surface.json     corpus-level roll-up + examples
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .acquire import repo_dir
from .analyze import (
    GRAPH_CONSTRUCTORS,
    GRAPH_READ_METHODS,
    _Analyzer,
    FileAnalysis,
)
from .config import RESULTS_RAW, RESULTS_SUMMARY, load_config, provenance
from .select import load_manifest

SURFACE_RAW = RESULTS_RAW / "surface.jsonl"
SURFACE_SUMMARY = RESULTS_SUMMARY / "surface.json"


def _excluded_repositories(cfg: dict, manifest: dict) -> dict[str, str]:
    """Repositories whose shapes must not be counted, and why.

    Three sources, in order of generality: the selection criteria themselves
    (a repository that no longer satisfies them — course material, a copy of
    the library, an abandoned project — is out), the post-analysis pruning,
    and finally an explicit list in ``[surface.excluded]`` for cases no
    criterion expresses.  Counting a repository's shapes is a stronger claim
    than keeping it in the corpus: what disqualifies these is not their code
    but the fact that counting them would break the independence of
    observations, or that their use of RDFLib is reflexive rather than
    applicative.
    """
    out: dict[str, str] = {}
    for name, rec in manifest.items():
        if not rec.get("selection_ok", True):
            reasons = ", ".join(rec.get("selection_reasons", [])) or "criteria"
            out[name] = f"does not satisfy the selection criteria ({reasons})"
        elif rec.get("pruned"):
            out[name] = f"pruned after analysis ({rec['pruned']})"
    out.update(cfg.get("surface", {}).get("excluded", {}))
    return out

# Selection methods that yield *terms* (as opposed to triples/quads).
TERM_SELECTORS = {
    "subjects", "objects", "predicates", "value",
    "transitive_objects", "transitive_subjects",
}
TUPLE_SELECTORS = {
    "triples", "quads", "subject_objects", "subject_predicates",
    "predicate_objects", "triples_choices", "items",
}
SELECTORS = TERM_SELECTORS | TUPLE_SELECTORS

# Builtins that consume an iterator; the name tells us what the caller wanted.
CONSUMERS = {"next", "list", "set", "sorted", "tuple", "len", "any", "all",
             "sum", "min", "max", "iter", "frozenset", "dict"}

QUERY_FORMS = ("select", "construct", "ask", "describe",
               "insert", "delete", "load", "clear", "drop", "create")

_PROLOGUE = re.compile(r"^\s*(?:@?(?:prefix|base)\s[^\n]*|#[^\n]*)\n",
                       re.IGNORECASE)


def _query_shape(text: str) -> str:
    """Classify a literal SPARQL query by its first keyword after the prologue."""
    body = text
    while True:
        stripped = _PROLOGUE.sub("", body, count=1)
        if stripped == body:
            break
        body = stripped
    head = body.strip().lower()
    for form in QUERY_FORMS:
        if head.startswith(form):
            return form
    return "other"


def _text_form(node: ast.expr) -> tuple[str, str | None]:
    """(how the query text is built, its literal text if constant)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return "literal", node.value
    if isinstance(node, ast.JoinedStr):          # f"..."
        return "fstring", None
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return "concat" if isinstance(node.op, ast.Add) else "percent", None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in ("format", "join", "substitute", "safe_substitute"):
            return "format", None
        if node.func.attr == "read":             # open(...).read()
            return "external", None
    if isinstance(node, ast.Name):
        return "variable", None
    if isinstance(node, ast.Attribute):
        return "variable", None
    return "other", None


@dataclass
class Surface:
    """Design-relevant shapes found in one file."""

    path: str
    repo: str = ""
    counts: Counter = field(default_factory=Counter)
    # Namespaces defined here: name -> IRI (empty string if not a literal)
    ns_defined: dict[str, str] = field(default_factory=dict)
    # Namespace-ish names imported from a non-rdflib (i.e. project) module
    ns_project_imports: list[str] = field(default_factory=list)
    # Imported namespace name -> IRI, when the exporting module is in the repo
    ns_imported_iris: dict[str, str] = field(default_factory=dict)
    # Uses of each namespace object, by local name
    ns_uses: Counter = field(default_factory=Counter)
    # Distribution of consecutive-`.add` run lengths: run length -> count
    add_runs: Counter = field(default_factory=Counter)
    # Run lengths where every add shares one subject expression
    add_runs_same_subject: Counter = field(default_factory=Counter)
    selectors: Counter = field(default_factory=Counter)
    selector_contexts: Counter = field(default_factory=Counter)
    query_forms: Counter = field(default_factory=Counter)
    query_text_forms: Counter = field(default_factory=Counter)
    graph_names: Counter = field(default_factory=Counter)
    examples: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "repo": self.repo,
            "counts": dict(sorted(self.counts.items())),
            "ns_defined": self.ns_defined,
            "ns_project_imports": sorted(set(self.ns_project_imports)),
            "ns_imported_iris": self.ns_imported_iris,
            "ns_uses": dict(sorted(self.ns_uses.items())),
            "add_runs": {str(k): v for k, v in sorted(self.add_runs.items())},
            "add_runs_same_subject": {
                str(k): v for k, v in sorted(self.add_runs_same_subject.items())},
            "selectors": dict(sorted(self.selectors.items())),
            "selector_contexts": dict(sorted(self.selector_contexts.items())),
            "query_forms": dict(sorted(self.query_forms.items())),
            "query_text_forms": dict(sorted(self.query_text_forms.items())),
            "graph_names": dict(sorted(self.graph_names.items())),
            "examples": self.examples,
        }


class _SurfaceVisitor(ast.NodeVisitor):
    """Second pass: record design-relevant shapes with bindings already known."""

    MAX_EXAMPLES = 4

    def __init__(self, surface: Surface, bindings, source_lines: list[str]) -> None:
        self.s = surface
        self.b = bindings
        self.lines = source_lines
        self.parents: dict[int, ast.AST] = {}
        self.depth_of_function: list[str] = []   # names of enclosing functions
        self.str_consts: dict[str, str] = {}     # name -> literal query text
        self.resolve_import = None               # set by surface_source
        self.counted_queries: set[str] = set()   # query texts already measured
        # Stack of variables bound by `for <vars> in g.<selector>(...)` loops
        self.selector_loop_vars: list[set[str]] = []

    # --- helpers -----------------------------------------------------------

    def _is_graph(self, expr: ast.expr) -> bool:
        if isinstance(expr, ast.Name):
            return expr.id in self.b.graph_vars
        if isinstance(expr, ast.Attribute):
            return expr.attr in self.b.graph_vars
        return False

    def _is_namespace(self, expr: ast.expr) -> bool:
        if isinstance(expr, ast.Name):
            return expr.id in self.b.namespace_vars
        if isinstance(expr, ast.Attribute):
            return expr.attr in self.b.namespace_vars
        return False

    def _receiver_name(self, expr: ast.expr) -> str:
        try:
            return ast.unparse(expr)
        except Exception:                       # pragma: no cover - defensive
            return "?"

    def _example(self, kind: str, node: ast.AST) -> None:
        if sum(1 for e in self.s.examples if e["kind"] == kind) >= self.MAX_EXAMPLES:
            return
        start = getattr(node, "lineno", 1)
        if any(e["kind"] == kind and e["line"] == start for e in self.s.examples):
            return
        end = getattr(node, "end_lineno", start) or start
        if end - start > 12:
            end = start + 12
        snippet = "\n".join(self.lines[start - 1:end])
        self.s.examples.append({"kind": kind, "line": start,
                                "snippet": snippet[:600]})

    # --- Q1: namespaces ----------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        from_rdflib = mod == "rdflib" or mod.startswith("rdflib.")
        if not from_rdflib:
            # A name imported from a project module and *exported there* as a
            # namespace object: direct evidence that namespaces are shared
            # code, which is what an `import ex:` construct would formalise.
            for alias in node.names:
                local = alias.asname or alias.name
                known_here = local in self.b.namespace_vars
                exported = None
                if self.resolve_import is not None:
                    exported = self.resolve_import(mod, node.level, alias.name)
                if exported is not None or known_here:
                    self.s.ns_project_imports.append(local)
                    self.s.counts["ns_imported_from_project"] += 1
                    if node.level:               # relative import
                        self.s.counts["ns_imported_relative"] += 1
                    if exported:
                        self.s.ns_imported_iris[local] = exported
                    self._example("ns_imported_from_project", node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._namespace_definition(node, node.value, node.targets)
        self._add_statement_shapes(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._namespace_definition(node, node.value, [node.target])
        self.generic_visit(node)

    def _namespace_definition(self, stmt: ast.stmt, value: ast.expr,
                              targets: list[ast.expr]) -> None:
        if not isinstance(value, ast.Call):
            return
        callee = self.b.rdflib_callee(value.func)
        if callee not in ("Namespace", "ClosedNamespace"):
            return
        iri = ""
        if value.args and isinstance(value.args[0], ast.Constant) and \
                isinstance(value.args[0].value, str):
            iri = value.args[0].value
        at_module_level = not self.depth_of_function
        self.s.counts["ns_def_total"] += 1
        self.s.counts["ns_def_module" if at_module_level else "ns_def_local"] += 1
        if not iri:
            self.s.counts["ns_def_computed_iri"] += 1
        for t in targets:
            if isinstance(t, ast.Name):
                self.s.ns_defined[t.id] = iri
        if at_module_level:
            self._example("ns_def_module", stmt)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for base in node.bases:
            name = self.b.rdflib_callee(base) or (
                base.id if isinstance(base, ast.Name) else None)
            if name == "DefinedNamespace":
                self.s.counts["ns_def_class"] += 1
                self.s.ns_defined.setdefault(node.name, "")
        self.depth_of_function.append(node.name)
        self.generic_visit(node)
        self.depth_of_function.pop()

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._is_namespace(node.value):
            self.s.ns_uses[self._receiver_name(node.value)] += 1
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if self._is_namespace(node.value):
            self.s.ns_uses[self._receiver_name(node.value)] += 1
            self.s.counts["ns_term_subscript"] += 1
        self.generic_visit(node)

    # --- functions ---------------------------------------------------------

    def _visit_function(self, node) -> None:
        self.depth_of_function.append(node.name)
        # Graphs in play inside this function body
        before = set(self.s.graph_names)
        self.generic_visit(node)
        gained = set(self.s.graph_names) - before
        if gained:
            self.s.counts["func_with_graph_ops"] += 1
            if len(gained) == 1:
                self.s.counts["func_single_graph"] += 1
        self.depth_of_function.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    # --- Q3: loop nesting over selectors -----------------------------------

    def _is_selector_call(self, expr: ast.expr) -> bool:
        return (isinstance(expr, ast.Call)
                and isinstance(expr.func, ast.Attribute)
                and expr.func.attr in SELECTORS
                and self._is_graph(expr.func.value))

    @staticmethod
    def _bound_names(target: ast.expr) -> set[str]:
        return {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}

    def _visit_loop(self, node) -> None:
        # The iterable is evaluated *outside* the loop it feeds, so it is
        # visited before its own target names enter scope.
        pushed = self._is_selector_call(node.iter)
        self.visit(node.iter)
        if pushed:
            self.selector_loop_vars.append(self._bound_names(node.target))
        for child in ast.iter_child_nodes(node):
            if child is not node.iter:
                self.visit(child)
        if pushed:
            self.selector_loop_vars.pop()

    def visit_For(self, node: ast.For) -> None:
        self._visit_loop(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_loop(node)

    def _visit_comp(self, node) -> None:
        """Comprehension generators: each one's iterable sees the previous
        generators' bindings, but not its own."""
        pushed = 0
        for gen in node.generators:
            is_sel = self._is_selector_call(gen.iter)
            self.visit(gen.iter)
            if is_sel:
                self.selector_loop_vars.append(self._bound_names(gen.target))
                pushed += 1
            for cond in gen.ifs:
                self.visit(cond)
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, ast.comprehension):
                self.visit(child)
        for _ in range(pushed):
            self.selector_loop_vars.pop()

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comp(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comp(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comp(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comp(node)

    # --- Q5: adds, run detection over statement lists ----------------------

    def _add_call(self, stmt: ast.stmt) -> tuple[str, ast.expr] | None:
        """(receiver, subject-expression) if the statement is a triple add."""
        if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
            return None
        call = stmt.value
        if not isinstance(call.func, ast.Attribute) or call.func.attr not in ("add", "set"):
            return None
        if not self._is_graph(call.func.value):
            return None
        if not call.args or not isinstance(call.args[0], ast.Tuple):
            return None
        if len(call.args[0].elts) != 3:
            return None
        return self._receiver_name(call.func.value), call.args[0]

    def _add_statement_shapes(self, node: ast.stmt) -> None:
        """Shapes of a lone add used as a value (``x = g.add(...)`` etc.)."""
        return  # adds are statements in practice; kept for symmetry

    def _term_is_static(self, expr: ast.expr) -> bool:
        """Can this term be written in Turtle without interpolating Python?

        Namespace terms (``EX.thing``), constant-argument constructors
        (``URIRef("http://…")``, ``Literal("x")``) and plain string constants
        qualify; anything computed does not.
        """
        if isinstance(expr, ast.Constant):
            return True
        if isinstance(expr, ast.Attribute):
            return self._is_namespace(expr.value)
        if isinstance(expr, ast.Subscript):
            return self._is_namespace(expr.value) and isinstance(expr.slice, ast.Constant)
        if isinstance(expr, ast.Call):
            callee = self.b.rdflib_callee(expr.func)
            if callee in ("URIRef", "Literal", "BNode"):
                return all(isinstance(a, ast.Constant) for a in expr.args) and \
                    all(isinstance(k.value, (ast.Constant, ast.Attribute))
                        for k in expr.keywords)
        return False

    def _scan_block(self, body: list[ast.stmt], *, in_loop: bool) -> None:
        """Find maximal runs of consecutive ``g.add((s, p, o))`` statements."""
        run: list[tuple[str, ast.expr, ast.stmt]] = []

        def flush() -> None:
            if not run:
                return
            n = len(run)
            self.s.add_runs[n] += 1
            self.s.counts["add_triples"] += n
            if in_loop:
                self.s.counts["add_in_loop"] += n
            recv = run[0][0]
            self.s.counts["add_receiver_chars"] += len(recv) * n
            if len(recv) > 3:
                self.s.counts["add_long_receiver"] += n
            first_line = getattr(run[0][2], "lineno", 0)
            last = run[-1][2]
            self.s.counts["add_run_lines"] += (
                (getattr(last, "end_lineno", first_line) or first_line)
                - first_line + 1)
            for _, triple, _stmt in run:
                if all(self._term_is_static(e) for e in triple.elts):
                    self.s.counts["add_terms_all_static"] += 1
                else:
                    self.s.counts["add_terms_computed"] += 1
            subjects = {self._receiver_name(t.elts[0]) for _, t, _ in run}
            if len(subjects) == 1:
                self.s.add_runs_same_subject[n] += 1
                if n > 1:
                    self.s.counts["add_run_shared_subject_triples"] += n
            if n == 1:
                self.s.counts["add_isolated"] += 1
            else:
                self.s.counts["add_in_run"] += n
                if n >= 3:
                    self._example("add_run", run[0][2])
            run.clear()

        for stmt in body:
            found = self._add_call(stmt)
            if found is None:
                flush()
            else:
                recv, subject = found
                if run and run[0][0] != recv:
                    flush()
                run.append((recv, subject, stmt))
        flush()

    def _walk_bodies(self, node: ast.AST, *, in_loop: bool = False) -> None:
        """Walk every statement-list, tracking whether we are inside a loop.

        A loop's ``body`` is inside the loop; its ``orelse`` is not (it runs
        at most once), and neither is the ``iter`` expression.
        """
        is_loop = isinstance(node, (ast.For, ast.AsyncFor, ast.While))
        for field_name, value in ast.iter_fields(node):
            inner = in_loop or (is_loop and field_name == "body")
            if field_name in ("body", "orelse", "finalbody") and \
                    isinstance(value, list) and value and \
                    isinstance(value[0], ast.stmt):
                self._scan_block(value, in_loop=inner)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self._walk_bodies(item, in_loop=inner)
            elif isinstance(value, ast.AST):
                self._walk_bodies(value, in_loop=inner)

    # --- calls: Q2, Q3, Q4, Q6 --------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        callee = self.b.rdflib_callee(node.func)
        if callee in GRAPH_CONSTRUCTORS:
            self.s.counts["graph_ctor"] += 1
            if callee in ("Dataset", "ConjunctiveGraph"):
                self.s.counts["graph_ctor_dataset"] += 1
            for kw in node.keywords:
                if kw.arg == "identifier":
                    self.s.counts["graph_named_identifier"] += 1
                    self._example("graph_named", node)
        if callee in ("prepareQuery", "prepareUpdate"):
            self.s.counts["sparql_prepare"] += 1
            self._query_call(node, prepared=True)
        if isinstance(node.func, ast.Attribute):
            self._method_call(node, node.func)
        self.generic_visit(node)

    def _method_call(self, node: ast.Call, func: ast.Attribute) -> None:
        method = func.attr
        if not self._is_graph(func.value):
            return
        self.s.graph_names[self._receiver_name(func.value)] += 1

        # --- Q2/Q4: SPARQL -------------------------------------------------
        if method in ("query", "update"):
            self.s.counts[f"sparql_{method}"] += 1
            self._query_call(node, prepared=False)
            self._query_consumption(node)
            return

        # --- Q6: named graph access ----------------------------------------
        if method in ("get_context", "graph", "contexts", "graphs"):
            self.s.counts["graph_named_access"] += 1
            return

        # --- Q3: selection / traversal -------------------------------------
        if method in SELECTORS:
            self.s.counts["trav_calls"] += 1
            self.s.selectors[method] += 1
            if method in TERM_SELECTORS:
                self.s.counts["trav_term_selector"] += 1
            else:
                self.s.counts["trav_tuple_selector"] += 1
            self._selector_context(node)
            self._selector_navigation(node)
        elif method in GRAPH_READ_METHODS:
            self.s.counts["trav_other_read"] += 1

    # --- Q2: query text and its consumption --------------------------------

    def _query_call(self, node: ast.Call, *, prepared: bool) -> None:
        arg = node.args[0] if node.args else None
        if arg is None:
            for kw in node.keywords:
                if kw.arg in ("query_object", "update_object"):
                    arg = kw.value
        if arg is not None:
            form, text = _text_form(arg)
            if text is None and isinstance(arg, ast.Name) and arg.id in self.str_consts:
                text, form = self.str_consts[arg.id], "literal_via_name"
            self.s.query_text_forms[form] += 1
            if text is not None:
                self.s.query_forms[_query_shape(text)] += 1
                nlines = text.count("\n") + 1
                self.s.counts["sparql_query_calls_literal"] += 1
                if text not in self.counted_queries:
                    # Source lines occupied by *distinct* query texts: what a
                    # SPARQL island would actually replace in this file.
                    self.counted_queries.add(text)
                    self.s.counts["sparql_query_lines"] += nlines
                    self.s.counts["sparql_queries_distinct"] += 1
                if nlines >= 3:
                    self._example("sparql_literal", node)
            else:
                self.s.query_forms["non_literal"] += 1
                if form in ("fstring", "concat", "percent", "format"):
                    self.s.counts["sparql_interpolated"] += 1
                    self._example("sparql_interpolated", node)
        for kw in node.keywords:
            if kw.arg == "initBindings":
                self.s.counts["bind_initbindings"] += 1
                self._example("bind_initbindings", node)
            elif kw.arg == "initNs":
                self.s.counts["bind_initns"] += 1

    def _query_consumption(self, node: ast.Call) -> None:
        parent = self.parents.get(id(node))
        if isinstance(parent, ast.For) and parent.iter is node:
            self.s.counts["sparql_consumed_for"] += 1
        elif isinstance(parent, ast.comprehension) and parent.iter is node:
            self.s.counts["sparql_consumed_comprehension"] += 1
        elif isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) \
                and parent.func.id in CONSUMERS:
            self.s.counts["sparql_consumed_builtin"] += 1
        elif isinstance(parent, (ast.Assign, ast.AnnAssign)):
            self.s.counts["sparql_assigned"] += 1

    # --- Q3: context and chaining of selectors -----------------------------

    def _selector_context(self, node: ast.Call) -> None:
        parent = self.parents.get(id(node))
        ctx = "other"
        if isinstance(parent, ast.For) and parent.iter is node:
            ctx = "for"
            self._example("trav_for", parent)
        elif isinstance(parent, ast.comprehension) and parent.iter is node:
            ctx = "comprehension"
            self._example("trav_comprehension", node)
        elif isinstance(parent, ast.Call):
            if isinstance(parent.func, ast.Name) and parent.func.id in CONSUMERS:
                ctx = parent.func.id
                if parent.func.id == "next":
                    self.s.counts["trav_single_value"] += 1
            elif isinstance(parent.func, ast.Attribute) and \
                    parent.func.attr in SELECTORS:
                ctx = "argument_of_selector"
        elif isinstance(parent, (ast.Assign, ast.AnnAssign)):
            ctx = "assign"
        elif isinstance(parent, (ast.Compare, ast.If, ast.IfExp)):
            ctx = "test"
        elif isinstance(parent, ast.Return):
            ctx = "return"
        self.s.selector_contexts[ctx] += 1

    def _selector_navigation(self, node: ast.Call) -> None:
        """Does this selector continue a traversal started by an enclosing one?

        Two shapes count as navigation, and the second is the common one:

          x = g.value(g.value(s, p), q)          # nested calls
          for s in g.subjects(...):              # nested loops, the result of
              for o in g.objects(s, ...):        # the outer feeding the inner
        """
        outer_vars = {name for frame in self.selector_loop_vars for name in frame}
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            for sub in ast.walk(arg):
                if isinstance(sub, ast.Name) and sub.id in outer_vars:
                    self.s.counts["trav_navigation_loop"] += 1
                    depth = len(self.selector_loop_vars)
                    self.s.counts[f"trav_navigation_depth_{min(depth, 4)}"] += 1
                    self._example("trav_navigation_loop", node)
                    return
        self._selector_chaining(node)

    def _selector_chaining(self, node: ast.Call) -> None:
        """A selector whose *argument* is itself a selector call: navigation."""
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            for sub in ast.walk(arg):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                        and sub.func.attr in SELECTORS and self._is_graph(sub.func.value):
                    self.s.counts["trav_chained"] += 1
                    self._example("trav_chained", node)
                    return

    # --- Q4: terms interpolated into query text ----------------------------

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        """f-strings that splice an RDF term into text (query building)."""
        spliced = False
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                expr = value.value
                if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
                        and expr.func.attr == "n3":
                    spliced = True
                elif self._is_namespace(expr) or (
                        isinstance(expr, ast.Attribute) and self._is_namespace(expr.value)):
                    spliced = True
        if spliced:
            self.s.counts["bind_term_interpolated"] += 1
            self._example("bind_term_interpolated", node)
        self.generic_visit(node)


def _record_parents(tree: ast.AST) -> dict[int, ast.AST]:
    parents: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


def _string_constants(tree: ast.AST) -> dict[str, str]:
    """Names bound to a literal string, anywhere in the module.

    SPARQL is very often held in a module-level constant (``QUERY = '''…'''``)
    or wrapped once by ``prepareQuery``; without this, such a call looks like
    an opaque ``variable`` and its query form cannot be classified.
    """
    consts: dict[str, str] = {}
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None:
            continue
        # unwrap prepareQuery("…") / prepareUpdate("…")
        if isinstance(value, ast.Call) and value.args:
            fname = value.func.attr if isinstance(value.func, ast.Attribute) \
                else getattr(value.func, "id", None)
            if fname in ("prepareQuery", "prepareUpdate"):
                value = value.args[0]
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            for t in targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = value.value
    return consts


def surface_source(source: str, path: str = "<string>", repo: str = "",
                   resolve_import=None) -> Surface:
    """Analyse one Python source text for design-relevant shapes.

    ``resolve_import(module, level, name) -> iri | None`` reports whether a
    name imported from a *project* module is a namespace object exported by
    that module; it is supplied by :func:`run` from a repository-wide index.
    """
    s = Surface(path=path, repo=repo)
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        s.counts["parse_error"] = 1
        return s
    # Reuse the validated name resolution of `analyze`: one binding pass first.
    seed = _Analyzer(FileAnalysis(path=path))
    seed.visit(tree)

    v = _SurfaceVisitor(s, seed.b, source.splitlines())
    v.parents = _record_parents(tree)
    v.str_consts = _string_constants(tree)
    v.resolve_import = resolve_import
    v.visit(tree)
    v._walk_bodies(tree)          # statement-level add runs

    if s.graph_names:
        s.counts["graphs_distinct"] = len(s.graph_names)
        if len(s.graph_names) == 1:
            s.counts["file_single_graph"] = 1
    if s.ns_defined:
        s.counts["ns_defined_here"] = len(s.ns_defined)
    return s


def surface_file(path: Path, repo: str = "") -> Surface:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        s = Surface(path=str(path), repo=repo)
        s.counts["read_error"] = 1
        return s
    return surface_source(source, str(path), repo)


# --- corpus-wide roll-up ---------------------------------------------------

def _exported_namespaces(source: str) -> dict[str, str]:
    """Module-level ``NAME = Namespace("iri")`` bindings of one module."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        return {}
    seed = _Analyzer(FileAnalysis(path="<index>"))
    seed.visit(tree)
    out: dict[str, str] = {}
    for stmt in tree.body:                       # module level only
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(stmt, ast.Assign):
            targets, value = stmt.targets, stmt.value
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            targets, value = [stmt.target], stmt.value
        elif isinstance(stmt, ast.ClassDef):
            for base in stmt.bases:
                name = seed.b.rdflib_callee(base) or (
                    base.id if isinstance(base, ast.Name) else None)
                if name == "DefinedNamespace":
                    out[stmt.name] = ""
            continue
        if not isinstance(value, ast.Call):
            continue
        if seed.b.rdflib_callee(value.func) not in ("Namespace", "ClosedNamespace"):
            continue
        iri = ""
        if value.args and isinstance(value.args[0], ast.Constant) and \
                isinstance(value.args[0].value, str):
            iri = value.args[0].value
        for t in targets:
            if isinstance(t, ast.Name):
                out[t.id] = iri
    return out


def build_namespace_index(root: Path, max_bytes: int = 2_000_000) -> dict[str, dict[str, str]]:
    """Repository-wide index: module path (POSIX, no ``.py``) -> exported namespaces.

    Only modules that export at least one namespace object are kept, so the
    index stays small even for large checkouts.
    """
    index: dict[str, dict[str, str]] = {}
    for path in root.rglob("*.py"):
        try:
            if path.stat().st_size > max_bytes:
                continue
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "Namespace" not in source and "DefinedNamespace" not in source:
            continue                              # cheap pre-filter
        exported = _exported_namespaces(source)
        if exported:
            rel = path.relative_to(root).with_suffix("")
            index[rel.as_posix()] = exported
    return index


def make_import_resolver(index: dict[str, dict[str, str]], file_rel: str):
    """Resolve ``from <module> import <name>`` against the repository index.

    Handles relative imports (``level`` dots up from the importing module's
    package) and absolute ones, which are matched as a path suffix so that a
    checkout rooted anywhere (``src/pkg/vocab.py``) still resolves.
    """
    here = Path(file_rel).parent

    def resolve(module: str, level: int, name: str) -> str | None:
        candidates: list[str] = []
        if level:
            base = here
            for _ in range(level - 1):
                base = base.parent
            target = base / Path(module.replace(".", "/")) if module else base
            candidates.append(target.as_posix())
            candidates.append((target / "__init__").as_posix())
            # `from . import vocab` style: the name itself is the module
            candidates.append((target / name).as_posix())
        elif module:
            dotted = module.replace(".", "/")
            candidates.append(dotted)
            candidates.append(dotted + "/__init__")
            for key in index:
                if key == dotted or key.endswith("/" + dotted) or \
                        key.endswith("/" + dotted + "/__init__"):
                    candidates.append(key)
        for cand in candidates:
            cand = cand.lstrip("./")
            exported = index.get(cand)
            if exported is not None and name in exported:
                return exported[name] or "?"
        return None

    return resolve


def _iter_rdf_files():
    """RDF-relevant files, from the analysis index produced by `analyze`."""
    index = RESULTS_RAW / "files_index.jsonl"
    if not index.exists():
        raise SystemExit("run `python -m rdfeval analyze` first: "
                         f"{index} is missing")
    with index.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("rdf_ops", 0) > 0 and not rec.get("error"):
                yield rec


def run(cfg=None) -> dict:
    """Analyse every RDF-relevant file and write raw + summary results.

    Files are visited grouped by repository so that each repository's
    namespace-export index is built once (Q1 needs cross-file evidence).
    """
    cfg = cfg or load_config()
    manifest = {r["full_name"]: r for r in load_manifest()}

    totals: Counter = Counter()
    selectors: Counter = Counter()
    selector_contexts: Counter = Counter()
    query_forms: Counter = Counter()
    query_text_forms: Counter = Counter()
    add_runs: Counter = Counter()
    add_runs_same_subject: Counter = Counter()
    ns_uses: Counter = Counter()
    # IRI -> {repo -> set(files)}: is the same namespace redefined repeatedly?
    ns_iri_files: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set))
    files_with: Counter = Counter()
    repos_with: dict[str, set[str]] = defaultdict(set)
    per_repo: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, list[dict]] = defaultdict(list)
    n_files = 0

    excluded = _excluded_repositories(cfg, manifest)
    skipped: Counter = Counter()

    by_repo: dict[str, list[dict]] = defaultdict(list)
    for rec in _iter_rdf_files():
        repo = rec["repository"]
        if repo in excluded:
            skipped[repo] += 1
            continue
        by_repo[repo].append(rec)

    SURFACE_RAW.parent.mkdir(parents=True, exist_ok=True)
    with SURFACE_RAW.open("w", encoding="utf-8") as out:
        for repo, records in sorted(by_repo.items()):
            if repo not in manifest:
                continue
            root = repo_dir(cfg, repo)
            if not root.exists():
                continue
            ns_index = build_namespace_index(root)
            for rec in records:
                path = root / rec["path"]
                if not path.exists():
                    continue
                resolver = make_import_resolver(ns_index, rec["path"])
                try:
                    source = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                s = surface_source(source, f"{repo}/{rec['path']}", repo,
                                   resolve_import=resolver)
                n_files += 1
                totals.update(s.counts)
                per_repo[repo].update(s.counts)
                selectors.update(s.selectors)
                selector_contexts.update(s.selector_contexts)
                query_forms.update(s.query_forms)
                query_text_forms.update(s.query_text_forms)
                add_runs.update(s.add_runs)
                add_runs_same_subject.update(s.add_runs_same_subject)
                ns_uses.update(s.ns_uses)
                for name, iri in s.ns_defined.items():
                    if iri:
                        ns_iri_files[iri][repo].add(rec["path"])
                for key in s.counts:
                    files_with[key] += 1
                    repos_with[key].add(repo)
                for ex in s.examples:
                    bucket = examples[ex["kind"]]
                    if len(bucket) < 12:
                        bucket.append({**ex, "path": s.path})
                out.write(json.dumps(s.to_dict(), ensure_ascii=False) + "\n")

    # Namespace duplication: the same IRI declared in several files of one
    # repository — the situation an `import ex:` construct would remove.
    dup_pairs = 0                  # (IRI, repo) declared in more than one file
    dup_files: set[tuple[str, str]] = set()
    cross_repo_iris = 0
    for iri, per_r in ns_iri_files.items():
        if len(per_r) > 1:
            cross_repo_iris += 1
        for repo, files in per_r.items():
            if len(files) > 1:
                dup_pairs += 1
                dup_files.update((repo, f) for f in files)

    # Guard against a single repository driving a conclusion: for the headline
    # counters, report how concentrated they are.
    def concentration(key: str) -> dict:
        vals = sorted((c.get(key, 0) for c in per_repo.values()), reverse=True)
        vals = [v for v in vals if v]
        total = sum(vals)
        return {
            "total": total,
            "repos": len(vals),
            "top_repo_share": round(vals[0] / total, 3) if total else 0.0,
            "median_per_repo": vals[len(vals) // 2] if vals else 0,
        }

    headline = ("add_triples", "add_isolated", "trav_calls", "sparql_query",
                "ns_def_module", "ns_imported_from_project", "bind_initbindings",
                "add_terms_all_static", "trav_navigation_loop")

    def ratio_across_repos(num, den, min_den: int = 10) -> dict:
        """Per-repository ratio, reported as a median.

        Corpus-wide ratios are dominated by whichever repository contributes
        the most operations — in this corpus, two near-duplicate course
        repositories contribute a third of all triple adds.  The median of the
        per-repository ratios is the robust reading; both are reported.
        """
        # `den` may be a tuple of keys that are summed (e.g. query + prepare)
        dens = (den,) if isinstance(den, str) else den
        def d(c):
            return sum(c.get(k, 0) for k in dens)
        ratios = sorted(c.get(num, 0) / d(c) for c in per_repo.values()
                        if d(c) >= min_den)
        total_num = sum(c.get(num, 0) for c in per_repo.values())
        total_den = sum(d(c) for c in per_repo.values())
        return {
            "pooled": round(total_num / total_den, 3) if total_den else 0.0,
            "median_per_repo": round(ratios[len(ratios) // 2], 3) if ratios else 0.0,
            "repos_counted": len(ratios),
        }

    summary = {
        "provenance": provenance(cfg),
        "files_analysed": n_files,
        "excluded_repositories": {
            repo: {"reason": reason, "rdf_files_skipped": skipped.get(repo, 0)}
            for repo, reason in sorted(excluded.items())},
        "totals": dict(sorted(totals.items())),
        "files_with": dict(sorted(files_with.items())),
        "repos_with": {k: len(v) for k, v in sorted(repos_with.items())},
        "concentration": {k: concentration(k) for k in headline},
        "ratios": {
            "adds_isolated": ratio_across_repos("add_isolated", "add_triples"),
            "adds_static_terms": ratio_across_repos("add_terms_all_static",
                                                    "add_triples"),
            "adds_in_loop": ratio_across_repos("add_in_loop", "add_triples"),
            "adds_shared_subject": ratio_across_repos(
                "add_run_shared_subject_triples", "add_triples"),
            "traversal_navigation": ratio_across_repos("trav_navigation_loop",
                                                       "trav_calls"),
            "queries_literal": ratio_across_repos(
                "sparql_query_calls_literal",
                ("sparql_query", "sparql_update", "sparql_prepare"), min_den=5),
        },
        "selectors": dict(sorted(selectors.items(), key=lambda kv: -kv[1])),
        "selector_contexts": dict(sorted(selector_contexts.items(),
                                         key=lambda kv: -kv[1])),
        "query_forms": dict(sorted(query_forms.items(), key=lambda kv: -kv[1])),
        "query_text_forms": dict(sorted(query_text_forms.items(),
                                        key=lambda kv: -kv[1])),
        "add_runs": {str(k): v for k, v in sorted(add_runs.items())},
        "add_runs_same_subject": {str(k): v for k, v in
                                  sorted(add_runs_same_subject.items())},
        "namespace_iris": {
            "distinct_iris": len(ns_iri_files),
            "iri_repo_pairs_declared_in_several_files": dup_pairs,
            "distinct_files_involved": len(dup_files),
            "iris_shared_across_repos": cross_repo_iris,
        },
        "top_namespaces_used": dict(sorted(ns_uses.items(),
                                           key=lambda kv: -kv[1])[:25]),
        "examples": dict(examples),
    }
    SURFACE_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SURFACE_SUMMARY.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _report(summary)
    return summary


def _report(summary: dict) -> None:
    """Print the headline shapes, as the other stages do."""
    t, fw = summary["totals"], summary["files_with"]
    skipped = sum(v["rdf_files_skipped"]
                  for v in summary["excluded_repositories"].values())
    print(f"surface: {summary['files_analysed']} files analysed "
          f"({skipped} skipped in {len(summary['excluded_repositories'])} "
          f"excluded repositories)")
    for key in ("ns_def_total", "ns_imported_from_project", "add_triples",
                "add_isolated", "add_terms_computed", "trav_calls",
                "trav_navigation_loop", "sparql_query", "sparql_prepare",
                "bind_initbindings"):
        print(f"  {key:26s} {t.get(key, 0):6d}  in {fw.get(key, 0):4d} files")
    print("  ratios (pooled / median per repository):")
    for key, r in summary["ratios"].items():
        print(f"    {key:24s} {r['pooled']:.3f} / {r['median_per_repo']:.3f}")


def main(argv=None) -> int:
    run(load_config())
    print(f"written: {SURFACE_RAW}, {SURFACE_SUMMARY}")
    return 0
