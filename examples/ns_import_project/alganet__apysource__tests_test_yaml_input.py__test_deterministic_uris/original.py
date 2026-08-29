# Extracted from alganet/apysource@f800ec97c1 : tests/test_yaml_input.py
# region: test_deterministic_uris (lines 192-199, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib.namespace import DCTERMS, RDF, RDFS
from apysource.namespaces import OA, SCHEMA, SV
from apysource.yaml_input import load_yaml, _slugify, _make_uri
SIMPLE_YAML = """\
sources:
  - label: "UN Charter"
    url: "https://www.un.org/en/about-us/un-charter/full-text"
    type: html
    language: en
    fragments:
      - label: "Preamble"
        selector: "p"
        snippet: "to save succeeding generations"
      - label: "Article 1"
        section: "Article 1"
        snippet: "The Purposes of the United Nations are"
"""

def test_deterministic_uris(tmp_path):
    """Same YAML produces identical URIs on repeated loads."""
    g1 = load_yaml(_write_yaml(tmp_path, SIMPLE_YAML))
    g2 = load_yaml(_write_yaml(tmp_path, SIMPLE_YAML))

    sources1 = sorted(str(s) for s in g1.subjects(RDF.type, SV.Source))
    sources2 = sorted(str(s) for s in g2.subjects(RDF.type, SV.Source))
    assert sources1 == sources2
