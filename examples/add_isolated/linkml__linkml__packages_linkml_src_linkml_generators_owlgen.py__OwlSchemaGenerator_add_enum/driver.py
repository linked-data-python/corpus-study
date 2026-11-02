"""Validation driver for linkml__linkml__packages_linkml_src_linkml_generators_owlgen.py__OwlSchemaGenerator_add_enum.

`add_enum(self, e)` writes the OWL axioms of one LinkML enum into
`self.graph`.  `self` is the REAL OwlSchemaGenerator of the pinned linkml
commit (context_shim.generator builds one from the YAML schema below and
prepares an empty graph, as as_graph() does); `e` is one of the schema's
EnumDefinitions.  What the original shows is the mutation of `self.graph`
(compared by isomorphism, with the rest of the generator's state), and the
warning it logs for a literal permissible value that has a meaning.

Each call exercises a different branch of the region, with the others'
enums in the same schema as neighbours that must not be written:

CALL_1  Animal       all PVs OWL classes (the default): subClassOf is the
                     sub_pred of the last loop; a PV with a meaning (IRI
                     from the curie), one with a space in its text
                     (percent-encoded IRI), metaclasses on (default)
CALL_2  Pet          is_a, two mixins (sorted) and `inherits`, defaults
CALL_3  Pet          same enum with enum_inherits_as_subclass_of and
                     mixins_as_expressions (existential restrictions)
CALL_4  Individuals  enum-level `implements: [owl:NamedIndividual]`:
                     sub_pred is rdf:type, combo_pred owl:oneOf
CALL_5  Texts        rdfs:Literal PVs: Literal nodes (no triple of their
                     own), and the warning logged for a meaning
CALL_6  Mixed        one PV implements owl:NamedIndividual among classes:
                     sub_pred stays dcterms:isPartOf; PV is_a and mixins,
                     add_root_classes on
CALL_7  Animal       metaclasses off
CALL_8  Empty        no permissible value (vacuous all([]))
"""
import context_shim
from rdfeval.harness import run_pair

SCHEMA = """
id: http://example.org/zoo
name: zoo
default_prefix: zoo
prefixes:
  zoo: http://example.org/zoo/
  ex: http://example.org/vocab/
  linkml: https://w3id.org/linkml/
imports:
  - linkml:types
enums:
  Animal:
    permissible_values:
      cat:
        meaning: ex:Cat
      dog: {}
      sea lion:
        description: has a space in its text
  Tagged:
    permissible_values:
      t1: {}
  Local:
    permissible_values:
      l1: {}
  Pet:
    is_a: Animal
    mixins: [Tagged, Local]
    inherits: [Animal]
    permissible_values:
      goldfish: {}
      hamster: {}
  Individuals:
    implements: [owl:NamedIndividual]
    permissible_values:
      i1: {}
      i2:
        meaning: ex:I2
  Texts:
    implements: [rdfs:Literal]
    permissible_values:
      hello: {}
      world:
        meaning: ex:World
  Mixed:
    permissible_values:
      m1: {}
      m2:
        implements: [owl:NamedIndividual]
      m3:
        is_a: m1
        mixins: [m2]
  Empty: {}
"""


def _call(enum, **options):
    def make():
        gen = context_shim.generator(SCHEMA, **options)
        return (gen, context_shim.enums(gen)[enum]), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="add_enum",
    calls=[
        _call("Animal"),
        _call("Pet"),
        _call("Pet", enum_inherits_as_subclass_of=True, mixins_as_expressions=True),
        _call("Individuals"),
        _call("Texts"),
        _call("Mixed", add_root_classes=True),
        _call("Animal", metaclasses=False),
        _call("Empty"),
    ],
)
