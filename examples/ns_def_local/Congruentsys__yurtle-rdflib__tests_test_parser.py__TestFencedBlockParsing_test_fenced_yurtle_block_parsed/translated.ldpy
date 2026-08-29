# Extracted from Congruentsys/yurtle-rdflib@8bbb378f5a : tests/test_parser.py
# region: TestFencedBlockParsing.test_fenced_yurtle_block_parsed (lines 203-211, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef
from yurtle_rdflib import PM, YURTLE, YurtleParser

def test_fenced_yurtle_block_parsed(self, sample_doc_with_fenced_blocks):
    """Fenced ```yurtle blocks should also be parsed."""
    parser = YurtleParser()
    doc = parser.parse(sample_doc_with_fenced_blocks)

    # The ```yurtle block has kb:statusChange triples
    kb = Namespace("https://yurtle.dev/kanban/")
    status_changes = list(doc.graph.triples((None, kb.statusChange, None)))
    assert len(status_changes) >= 1
