# Extracted from kumagallium/asterism@f0977d4d3a : ingest/tests/test_documents.py
# region: test_identity_and_parse_activity (lines 141-151, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib
from asterism.documents import (
    DOCO,
    LIT,
    NIF,
    ConversionError,
    JatsDocumentError,
    convert_docx_to_jats,
    derive_doc_id,
    pandoc_version,
    sentence_spans,
    structure_jats,
)
BASE = "https://kumagallium.github.io/asterism/papers/resource/document/ds/PMC-TEST"

def test_identity_and_parse_activity() -> None:
    g = _g()
    paper = rdflib.URIRef(BASE)
    assert str(g.value(paper, rdflib.URIRef(LIT + "pmcid"))) == "PMC-TEST"
    ident = rdflib.URIRef("http://purl.org/dc/terms/identifier")
    assert str(g.value(paper, ident)) == "10.1234/demo"
    act = g.value(paper, rdflib.URIRef("http://www.w3.org/ns/prov#wasGeneratedBy"))
    assert (act, rdflib.RDF.type, rdflib.URIRef(LIT + "DocumentParsingActivity")) in g
    # endedAtTime comes from the document's pub-date (deterministic, never now()).
    ended = rdflib.URIRef("http://www.w3.org/ns/prov#endedAtTime")
    assert "2020-03-04" in str(g.value(act, ended))
