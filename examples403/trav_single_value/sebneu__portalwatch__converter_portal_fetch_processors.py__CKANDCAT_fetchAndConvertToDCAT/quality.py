# Context shim (see meta.json): stand-in for portalwatch's top-level
# quality.py (sebneu/portalwatch@a514eba7bfb21c62ac75ad4745a28435475021d5), a
# real top-level module -- fetchAndConvertToDCAT does a plain `import
# quality`, not an import from converter.dataset_converter, hence a separate
# file here rather than another name in context_shim.py.
#
# add_quality_measures's real body reads DCAT/DCT/VCARD properties off each
# dataset and writes DQV measure triples for them; that logic is unrelated to
# what this region's own trav_single_value sites read (hydra pagination) and
# pulls in three more portalwatch utility modules (ODM_formats,
# licenses_mapping, IANA_formats). It is called identically -- same
# arguments, same call sites -- by both original.py and translated.ldpy, so a
# no-op stand-in preserves the comparison: whatever it would have added to
# `graph` is added on neither side alike, rather than reproduced correctly on
# one side and not the other.
def add_quality_measures(dataset_uri, graph, act):
    pass
