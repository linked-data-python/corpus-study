# Extracted from kumagallium/asterism@f0977d4d3a : experiments/pdf-docling-spike/run_spike.py
# region: main (lines 145-197, stratum sparql_literal)
# licence of the source repository: see meta.json
HERE = Path(__file__).resolve().parent
DOCO = "http://purl.org/spar/doco/"
NIF = "http://persistence.uni-leipzig.de/nlp2rdf/ontologies/nif-core#"
CONVERTER = "docling/2.101.0 (docling-ibm-models/3.13.3)"

def main() -> int:
    sections = parse_markdown((HERE / "ma11040649.docling.md").read_text(encoding="utf-8"))
    ttl = build_turtle(sections)
    import rdflib

    g = rdflib.Graph()
    g.parse(data=ttl, format="turtle")
    n_sec = len(list(g.subjects(rdflib.RDF.type, rdflib.URIRef(DOCO + "Section"))))
    n_para = len(list(g.subjects(rdflib.RDF.type, rdflib.URIRef(DOCO + "Paragraph"))))
    n_sent = len(list(g.subjects(rdflib.RDF.type, rdflib.URIRef(DOCO + "Sentence"))))
    print(f"PDF -> Docling -> doco/nif graph: {len(g)} triples "
          f"({n_sec} sections, {n_para} paragraphs, {n_sent} sentences)")

    # the headline: find the SAME measurement-condition sentence the JATS path cited,
    # via the SAME kind of full-text-down-to-the-sentence query.
    rows = list(g.query(
        """
        PREFIX doco: <http://purl.org/spar/doco/>
        PREFIX po: <http://www.essepuntato.it/2008/12/pattern#>
        PREFIX nif: <http://persistence.uni-leipzig.de/nlp2rdf/ontologies/nif-core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX lit: <https://kumagallium.github.io/asterism/papers/ontology#>
        SELECT ?sent ?text ?path ?title ?conv WHERE {
          ?sent a doco:Sentence ; nif:anchorOf ?text ; prov:wasGeneratedBy ?parse .
          ?para po:contains ?sent . ?sec po:contains ?para ; dcterms:title ?title .
          OPTIONAL { ?sec lit:structuralPath ?path }
          ?parse prov:wasInformedBy ?conv .
          FILTER(CONTAINS(?text, "physical properties measurement system"))
        }
        """
    ))
    assert rows, "PPMS sentence not recovered from the PDF path"
    sent, text, path, title, conv = (str(x) for x in rows[0])
    print("\nCITATION recovered from the PDF (no JATS):")
    print(f"  §{path} / {title}")
    print(f"  “{text}”")
    print(f"  IRI: {sent}")
    print(f"  via conversion: {conv.rsplit('/', 2)[-2]} ({CONVERTER})")

    # cross-check: the JATS path cited the SAME verbatim (the two sources agree).
    jats = rdflib.Graph()
    jats.parse(HERE.parents[1] / "datasets" / "papers" / "seed" / "paper.ttl", format="turtle")
    jats_ppms = [str(o) for s, p, o in jats.triples((None, rdflib.URIRef(NIF + "anchorOf"), None))
                 if "physical properties measurement system" in str(o)]
    agree = bool(jats_ppms) and jats_ppms[0].strip() == text.strip()
    print(f"\nPDF-derived sentence == JATS-derived sentence (same citable fact): "
          f"{'✓ IDENTICAL' if agree else '≈ (see both)'}")
    if not agree and jats_ppms:
        print(f"  JATS: “{jats_ppms[0]}”")
    print("\nOK: an unstructured PDF, via a provenance-recorded conversion, lands in the "
          "same citable document graph as JATS — down to the sentence.")
    return 0 if agree else 1
