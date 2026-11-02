# Context shim (see meta.json): what surrounds OwlSchemaGenerator.add_enum in
# linkml/linkml@680595df54 : packages/linkml/src/linkml/generators/owlgen.py.
#
# `add_enum(self, e)` is a method of the real OwlSchemaGenerator and needs the
# generator's other methods (_enum_uri, add_metadata, _get_metatype,
# _permissible_value_uri, _literal, _boolean_expression, ...) and a real
# SchemaView.  linkml and linkml_runtime are imported from the pinned clone
# made by `rdfeval acquire` (corpus/repos/linkml__linkml, packages/linkml/src
# and packages/linkml_runtime/src), i.e. the REAL code of that commit; their
# third-party dependencies (deprecated, hbreader, jsonasobj2, curies,
# prefixcommons, pydantic, ...) must be installed in the interpreter.
# Identical bindings for both representations.
#
# `generator(schema_yaml, **options)` builds an OwlSchemaGenerator from a
# schema given as a YAML string and prepares what as_graph() prepares before
# it calls add_enum: an empty `graph` and the ontology header, and returns it
# behind `_Self`, a transparent proxy: every attribute and method is the real
# generator's (so the region runs the real _enum_uri, add_metadata,
# _boolean_expression, ... on the real graph), except that the proxy's own
# state is the `graph` alone.  This is only so that the evaluation harness,
# which compares what a call did to its arguments by walking their
# attributes, compares the generator's graph instead of recursing through a
# SchemaView.  `enums(gen)` returns the schema's EnumDefinitions by name.
import sys
from pathlib import Path

_PACKAGES = Path(__file__).resolve().parents[3] / "corpus" / "repos" / "linkml__linkml" / "packages"
for _src in (_PACKAGES / "linkml" / "src", _PACKAGES / "linkml_runtime" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from rdflib import Graph, URIRef, OWL, RDF  # noqa: E402

from linkml.generators.owlgen import OwlSchemaGenerator  # noqa: E402


_GENERATORS = {}


class _Self:
    def __init__(self, gen):
        self.graph = gen.graph
        _GENERATORS[id(self)] = gen

    def __getattr__(self, name):
        return getattr(_GENERATORS[id(self)], name)


def generator(schema_yaml, **options):
    gen = OwlSchemaGenerator(schema_yaml, **options)
    # as_graph() starts from these three lines (deprecation defaults) and a
    # fresh Graph(identifier=base) before adding anything
    gen.skip_vacuous_min_zero_cardinality_axioms = False
    gen.skip_vacuous_local_range_axioms = False
    gen.consolidate_cardinality_axioms = False
    base = URIRef(gen.schemaview.schema.id)
    gen.graph = Graph(identifier=base)
    gen.graph.add((base, RDF.type, OWL.Ontology))
    return _Self(gen)


def enums(gen):
    return gen.schemaview.all_enums()
