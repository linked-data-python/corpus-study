# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_sparql12_query.py
# region: TestQ11.test_ask_true (lines 352-360, stratum sparql_literal)
# licence of the source repository: see meta.json
def test_ask_true(self, g):
    # << >> (reification shorthand) in SPARQL matches via reifier of the triple
    r = g.query("""
        PREFIX :   <http://example.org/>
        ASK {
          << :bob :knows :carol >> :verifiedBy :ResearchTeam .
        }
    """)
    assert r.askAnswer is True
