# Extracted from pangenome/spodgi@6d7d944f38 : test/test_select.py
# region: test_count_distinct_steps (lines 64-74, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.store import Store
from rdflib import Graph
from rdflib import plugin

def test_count_distinct_steps():
    plugin.register('OdgiStore', Store, 'spodgi.OdgiStore', 'OdgiStore')
    s = plugin.get('OdgiStore', Store)(base="http://example.org/test/")
    spodgi = Graph(store=s)
    spodgi.open('./test/t.odgi', create=False)
    for r in spodgi.query('''PREFIX vg:<http://biohackathon.org/resource/vg#>
    SELECT (count(distinct ?s) as ?count) WHERE {?s a vg:Step}'''):
        assert r[0].value == 10

    spodgi.close()
    assert True
