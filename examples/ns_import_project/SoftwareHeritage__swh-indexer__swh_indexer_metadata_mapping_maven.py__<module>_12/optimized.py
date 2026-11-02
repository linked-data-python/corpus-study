# Extracted from SoftwareHeritage/swh-indexer@95f3e65462 : swh/indexer/metadata_mapping/maven.py
# region: <module> (lines 12-12, stratum ns_import_project)
# licence of the source repository: see meta.json
#
# Executability restoration (AGENT_BATCH "163 regions" case, see meta.json):
# `swh.indexer.namespaces` rewritten to `swh_namespaces_context`, the shim
# module next to this file (`swh.indexer` is not installed in this venv --
# verified, `ModuleNotFoundError` -- so the real dotted path does not
# resolve for a single extracted file).
from swh_namespaces_context import SCHEMA


# Demo harness (identical on both sides, see meta.json): this region is a
# single import line with rdf_ops=0 -- it binds a name but performs no
# graph operation of its own, so there is nothing for the harness's default
# module-state comparison to observe UNLESS the bound namespace is actually
# dereferenced (the prefix import leaves no module-level Python name at all
# -- declarations.md: "no name is captured"). demo() dereferences the one
# real term used elsewhere in maven.py at the pinned commit
# (SCHEMA.codeRepository, swh/indexer/metadata_mapping/maven.py:81) and
# returns its string form.
def demo():
    return str(SCHEMA.codeRepository)
