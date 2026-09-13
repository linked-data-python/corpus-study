"""Validation driver for calipho-sib__nextprot-scripts__src_polish-rdf_pylode_pyLODE-2.13.2_pylode_profiles_base.py__BaseProfile__make_schemaorg_metadata.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
class _Fake:
    """Minimal stand-in for BaseProfile: only the two attributes the
    region reads (METADATA, outputformat)."""

    def __init__(self):
        self.outputformat = "other"
        self.METADATA = {
            "uri": "http://ex.org/doc",
            "title": "Test Doc",
            "created": "2020-01-01",
            "date_created": "yes",
            "modified": "2020-02-02",
            "description": "A description",
            "license": '"http://license.org/lic"',
            "rights": "Some rights",
            "copyright_year": "yes",
            "repository": '"http://ex.org/repo"',
        }

    def __eq__(self, other):
        return (isinstance(other, _Fake)
                and self.outputformat == other.outputformat
                and self.METADATA == other.METADATA)


def _fixture():
    return ((_Fake(),), {})


VERDICT = run_pair(
    __file__,
    entry='_make_schemaorg_metadata',
    calls=[_fixture],
)
