# Context shim (see meta.json): subset of
# semantic-model/shacl2flink/lib/shacl_properties_to_sql.py from
# IndustryFusion/DigitalTwin@3b40088b880811f61df63ba926f78256098ce695, so the
# region executes outside the package. Identical bindings for both
# representations.
#
# VALUE_PATH_ATTRIBUTE_TYPES is the module-level constant the region's own
# `NGSILD_VALUE_PATHS = frozenset(VALUE_PATH_ATTRIBUTE_TYPES)` line (kept in
# original.py/translated.ldpy, not moved here) closes over, copied verbatim
# from around line 1693 of the source file.
#
# connective_clauses(g, node) is the helper the region calls
# (`frontier.extend(connective_clauses(g, shape))`) to walk sh:and / sh:or /
# sh:xone list members and sh:not branches, copied verbatim from around line
# 1729 -- together with the LIST_CONNECTIVES constant it closes over. It is
# NOT part of the region under study (it sits earlier in the same source
# file, its own separate top-level function) and is left untranslated: it
# stays plain rdflib, exactly as the pipeline's context window shows a
# called-but-not-extracted function.
from rdflib.collection import Collection
from rdflib.namespace import SH

# Value path -> the NGSI-LD attribute type it implies.
VALUE_PATH_ATTRIBUTE_TYPES = {
    'https://uri.etsi.org/ngsi-ld/hasValue': 'https://uri.etsi.org/ngsi-ld/Property',
    'https://uri.etsi.org/ngsi-ld/hasValueList': 'https://uri.etsi.org/ngsi-ld/ListProperty',
    'https://uri.etsi.org/ngsi-ld/hasJSON': 'https://uri.etsi.org/ngsi-ld/JsonProperty',
    'https://uri.etsi.org/ngsi-ld/hasObject': 'https://uri.etsi.org/ngsi-ld/Relationship',
}

LIST_CONNECTIVES = ((SH['and'], 'AND'), (SH['or'], 'OR'), (SH.xone, 'XONE'))


def connective_clauses(g, node):
    """Every branch of every connective directly on this node."""
    for predicate, _ in LIST_CONNECTIVES:
        for collection in g.objects(node, predicate):
            for branch in Collection(g, collection):
                yield branch
    for branch in g.objects(node, SH['not']):
        yield branch
