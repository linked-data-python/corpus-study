# Extracted from openworm/owmeta-core@cd69d77ad0 : owmeta_core/dataobject.py
# region: <module> (lines 634-634, stratum ns_def_local)
# licence of the source repository: see meta.json
#
# `from . import ...` (a package-relative import into owmeta_core/__init__.py)
# is replaced by `from context_shim import ...` so the region resolves
# outside the owmeta_core package -- same four names, see meta.json /
# AGENT_BATCH.md "shim de contexte". The real source line
# (owmeta_core/dataobject.py:634) is a class attribute of BaseDataObject, not
# a bare module-level statement -- see translation_notes.
import rdflib as R
from context_shim import BASE_DATA_URL, BASE_SCHEMA_URL, DEF_CTX, RDF_CONTEXT

base_data_namespace = R.Namespace(BASE_DATA_URL + "/")
