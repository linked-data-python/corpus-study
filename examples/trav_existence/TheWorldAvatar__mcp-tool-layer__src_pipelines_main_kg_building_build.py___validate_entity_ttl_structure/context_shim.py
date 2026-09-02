# Context shim (see meta.json): `_validate_entity_ttl_structure` calls
# `_resolve_expected_top_entity_uri`, defined in the SAME source file
# (src/pipelines/main_kg_building/build.py:125-176 at
# TheWorldAvatar/mcp-tool-layer@c440a33e08) but well outside the extracted
# region (854-914), and itself depending on three more helpers
# (`_normalize_entity_label_key`, `_first_label`,
# `_choose_preferred_typed_target`) that disambiguate `top_entity` by
# label-matching when the graph holds SEVERAL candidate subjects of the
# expected class. That disambiguation is not part of this region and is not
# an RDF-existence read this stratum measures, so it is not reproduced in
# full here.
#
# What IS reproduced, verbatim, is the real function's own behaviour for the
# case this study's fixtures actually exercise: the caller supplies
# `entity_uri` directly and the graph does not need disambiguating (either
# because it holds no OTHER same-class candidate, or because `entity_uri`
# is already the single candidate) -- confirmed against build.py:139-140
# (`explicit_uri = str(entity_uri or "").strip(); ... if explicit_ref in
# typed_entities: return explicit_uri`) and :175-176 (the final fallback,
# `return explicit_uri`, taken whenever no label match was found and there
# is not EXACTLY one typed candidate). Both of the real function's own exit
# points that this region's fixtures reach return `entity_uri` unchanged, so
# the shim does exactly that and nothing else.
def _resolve_expected_top_entity_uri(
    g, *, top_class_iri, entity_uri="", entity_label="",
    label_key_suffixes_to_strip=None,
):
    return str(entity_uri or "").strip()
