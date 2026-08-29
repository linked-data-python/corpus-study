# Extracted from linkml/linkml@680595df54 : packages/linkml/src/linkml/generators/shaclgen.py
# region: ShaclGenerator._add_rules (lines 419-490, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SH, XSD
from linkml_runtime.linkml_model.meta import ClassDefinition, ElementName, PresenceEnum
logger = logging.getLogger(__name__)

def _add_rules(self, g: Graph, shape_uri: URIRef, cls: ClassDefinition) -> None:
    """Emit ``sh:sparql`` constraints from LinkML ``rules:`` blocks.

    Each recognised rule is converted into an ``sh:SPARQLConstraint``
    attached to *shape_uri*.  Unrecognised patterns are logged at
    ``DEBUG`` level and silently skipped.

    Currently recognised patterns:

    * **Boolean guard** — a *precondition* with
      ``value_presence: PRESENT`` on a value slot and a *postcondition*
      with ``equals_string: "true"`` on a boolean flag slot.

    * **Exclusive value** — a *precondition* with ``equals_string`` on
      a slot and a *postcondition* with ``maximum_cardinality`` on the
      *same* slot.  Enforces that when a specific value is present in a
      multivalued slot, the total number of values must not exceed the
      given cardinality (typically 1 for mutual exclusion).

    See `W3C SHACL §5 <https://www.w3.org/TR/shacl/#sparql-constraints>`_.
    """
    if not cls.rules:
        return

    sv = self.schemaview
    for rule in cls.rules:
        if getattr(rule, "deactivated", False):
            continue

        if getattr(rule, "bidirectional", False):
            logger.warning(
                "Rule in class %r has bidirectional=true; "
                "SHACL-SPARQL generation does not support bidirectional rules. "
                "Skipping this rule entirely.",
                cls.name,
            )
            continue

        if getattr(rule, "open_world", False):
            logger.warning(
                "Rule in class %r has open_world=true; "
                "SHACL operates under closed-world assumption. "
                "The constraint is emitted but may not match open-world semantics.",
                cls.name,
            )

        if getattr(rule, "elseconditions", None):
            logger.warning(
                "Rule in class %r has elseconditions; "
                "only the forward (if/then) branch is emitted as sh:sparql. "
                "The else branch cannot be represented in SHACL-SPARQL.",
                cls.name,
            )

        sparql_query = self._rule_to_sparql(sv, cls, rule)
        if sparql_query is None:
            logger.debug(
                "Skipping unsupported rule pattern in class %r: %s",
                cls.name,
                getattr(rule, "description", "(no description)"),
            )
            continue

        constraint = BNode()
        g.add((shape_uri, SH.sparql, constraint))
        g.add((constraint, RDF.type, SH.SPARQLConstraint))

        message = getattr(rule, "description", None)
        if message:
            g.add((constraint, SH.message, Literal(message)))

        g.add((constraint, SH.select, Literal(sparql_query)))
