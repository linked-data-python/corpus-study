"""Validation driver for lazlop__semantic_objects__.claude_worktrees_watr-ingestion_src_semantic_objects_exporters.py__RdfExporter_generate_rdf_class_definition.

The region is a statement-level excerpt that builds the graph `g` (oracle:
isomorphism, plus the module-level `processed_relations` set, which is a
module value compared by name).  The program is executed once per side, so
what the region exercises is decided by the data in context_shim.py
(`_SourceThing._valid_relations`), not by arguments.  Its six relations are
chosen so that every branch the region can reach is taken at least once:

  * `hasNothing`, target None: the "None" name, and no `sh:class`/`sh:message`
    (the target has no `_get_iri`);
  * `hasTarget`, a Resource subclass: `target_class.__name__`, and the
    `sh:class` + `sh:message` triples;
  * `hasPlain`, a class without `_get_iri`: `__name__` branch, comment only;
  * `hasSelf`, `typing.Self` (as the repo writes self-referential relations):
    the `Self` branch, which rebinds `target_class = cls`, read afterwards for
    `sh:class` and for the message text;
  * the second `hasTarget` and second `hasSelf`: the `processed_relations`
    de-duplication (a repeated predicate must not make a second shape);
  * not exercised, and not reachable from this excerpt: the `else` branch
    (`str(target_class)`), because `target_class.__name__` on the line before
    raises AttributeError for any object without `__name__`; and the
    `hasattr(base_class, '_valid_relations')` guard, because the restored
    binding is `classes_to_process = [cls]` and `cls` has the attribute (the
    real method walks `cls.__mro__` when `include_hierarchy` is set).
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
