# Context shim (see meta.json): a stand-in for the module-level `args`
# (an argparse.Namespace, built elsewhere in
# recipe-importer/rdflib/tools/defined_namespace_creator.py) that
# get_target_namespace_elements reads via `args.target_namespace` even
# though the function itself already receives `target_namespace` as a
# parameter -- a genuine dangling global reference in the source, kept
# as-is (no refactor). Mutable so the driver can set it per call.
# Identical binding for both representations.
class _Args:
    target_namespace = ""


args = _Args()
