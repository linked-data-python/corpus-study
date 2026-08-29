# Extracted from OAI/oascomply@9f41627512 : oascomply/oasgraph.py
# region: OasGraph.__init__ (lines 72-94, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib

def __init__(self, version: str, *, test_mode=False):
    if version not in ('3.0', '3.1'):
        raise ValueError(f'OAS v{version} is not supported.')
    if version == '3.1':
        raise ValueError(f'OAS v3.1 support TBD.')
    self._version = version
    self._test_mode = test_mode

    self._g = rdflib.Graph()
    self._oas_unversioned = rdflib.Namespace(
        'https://spec.openapis.org/compliance/ontology#'
    )
    self._oas_versions = {
        '3.0': rdflib.Namespace(
            'https://spec.openapis.org/compliance/ontology#3.0-'
        ),
        '3.1': rdflib.Namespace(
            'https://spec.openapis.org/compliance/ontology#3.1-'
        ),
    }
    self._g.bind('oas', self._oas_unversioned)
    self._g.bind('oas3.0', self._oas_versions['3.0'])
    self._g.bind('oas3.1', self._oas_versions['3.1'])
