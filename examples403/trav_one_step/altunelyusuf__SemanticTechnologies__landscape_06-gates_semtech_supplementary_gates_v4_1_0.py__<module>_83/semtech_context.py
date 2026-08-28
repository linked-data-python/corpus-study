# Context shim (see meta.json): the region references EC.KIND_DEFNS, where
# EC is landscape/07-tooling/enrichment_c_v2_0_0.py from
# altunelyusuf/SemanticTechnologies@bad0fa7c46af8bac1b27eec8b89660de5e69f85e,
# loaded by the source file at run time through
# importlib.util.spec_from_file_location("enrichment_c", ".../enrichment_c_v2_0_0.py")
# (see the module's own header, above the extracted lines). That dynamic
# loading — and the sibling taxonomy/enrichment/registry modules it draws
# from — is out of reach here, so this shim reproduces just the one binding
# the region actually reads: the 14 keys of KIND_DEFNS (a dict of
# name -> prose definition in the source; only the keys drive the region's
# logic, so the prose is dropped). Identical bindings for both
# representations.
class _EC:
    KIND_DEFNS = [
        "Tool", "Library", "Framework", "Platform", "Standard", "Method",
        "Technique", "Practice", "Case", "Body", "Regulation", "Benchmark",
        "Trend", "Concept",
    ]


EC = _EC()
