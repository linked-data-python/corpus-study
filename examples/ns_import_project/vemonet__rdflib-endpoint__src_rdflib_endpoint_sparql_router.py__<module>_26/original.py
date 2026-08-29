# Extracted from vemonet/rdflib-endpoint@1427c77829 : src/rdflib_endpoint/sparql_router.py
# region: <module> (lines 26-37, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib_endpoint.utils import (
    API_RESPONSES,
    FORMATS,
    GENERIC_CONTENT_TYPE_TO_RDFLIB_FORMAT,
    GRAPH_CONTENT_TYPE_TO_RDFLIB_FORMAT,
    SD,
    SPARQL_RESULT_CONTENT_TYPE_TO_RDFLIB_FORMAT,
    Defaults,
    QueryExample,
    get_default_content_type,
    parse_accept_header,
)
