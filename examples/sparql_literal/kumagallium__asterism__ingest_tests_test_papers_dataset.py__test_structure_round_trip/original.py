# Extracted from kumagallium/asterism@f0977d4d3a : ingest/tests/test_papers_dataset.py
# region: test_structure_round_trip (lines 121-159, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib
PAPER = "https://kumagallium.github.io/asterism/papers/resource/paper/PMC5951533"

def test_structure_round_trip() -> None:
    g = rdflib.Graph()
    g.parse(data=_seed_ttl(), format="turtle")
    # Downward: paper -> section -> paragraph -> sentence, all via po:contains.
    down = list(
        g.query(
            """
            PREFIX po: <http://www.essepuntato.it/2008/12/pattern#>
            PREFIX doco: <http://purl.org/spar/doco/>
            SELECT ?sec ?para ?sent WHERE {
              ?paper po:contains ?sec . ?sec a doco:Section ; po:contains ?para .
              ?para a doco:Paragraph ; po:contains ?sent . ?sent a doco:Sentence .
            } LIMIT 1
            """,
            initBindings={"paper": rdflib.URIRef(PAPER)},
        )
    )
    assert down, "no paper -> sec -> para -> sentence containment path"
    sec, para, sent = (str(x) for x in down[0])
    # Upward from the sentence: its paragraph, its section, the paper it was quoted
    # from, and its NIF reference context — both up-links the gate names.
    up = list(
        g.query(
            """
            PREFIX po: <http://www.essepuntato.it/2008/12/pattern#>
            PREFIX nif: <http://persistence.uni-leipzig.de/nlp2rdf/ontologies/nif-core#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT ?para ?sec ?paper ?ctx WHERE {
              ?para po:contains ?sent . ?sec po:contains ?para .
              ?sent prov:wasQuotedFrom ?paper ; nif:referenceContext ?ctx .
            } LIMIT 1
            """,
            initBindings={"sent": rdflib.URIRef(sent)},
        )
    )
    assert up, "cannot walk back up from the sentence"
    u_para, u_sec, u_paper, ctx = (str(x) for x in up[0])
    assert u_para == para and u_sec == sec and u_paper == PAPER
    assert ctx == PAPER + "/fulltext"
