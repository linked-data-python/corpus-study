# Extracted from openworm/owmeta-core@cd69d77ad0 : owmeta_core/dataobject.py
# region: <module> (lines 634-634, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib as R
from . import BASE_DATA_URL, BASE_SCHEMA_URL, DEF_CTX, RDF_CONTEXT

base_data_namespace = R.Namespace(BASE_DATA_URL + "/")
