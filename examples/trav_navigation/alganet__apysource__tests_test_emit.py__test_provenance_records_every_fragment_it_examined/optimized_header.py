# Extracted from alganet/apysource@f800ec97c1 : tests/test_emit.py
# region: test_provenance_records_every_fragment_it_examined (lines 191-204, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import RDF
from apysource.namespaces import PROV, SV
from provenance_shim import _run_with_provenance
def test_provenance_records_every_fragment_it_examined():
    """Including the failures.

    Several failure paths returned before recording anything, so a fragment the
    run had examined and rejected was simply absent — indistinguishable from one
    the run never reached. A file that omits its failures is not a record.
    """
    _, prov = _run_with_provenance()
    verdicts = {
        str(prov.value(v, PROV.wasDerivedFrom)): str(prov.value(v, SV.verificationStatus))
        for v in prov.subjects(RDF.type, SV.VerificationResult)
    }
    assert sorted(verdicts.values()) == ["failed", "verified"]
