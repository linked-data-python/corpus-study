# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_fdo_nanopub.py
# region: test_add_fdo_profile (lines 82-89, stratum ns_import_project)
# licence of the source repository: see meta.json
import pytest
import rdflib
from rdflib import RDF, RDFS, DCTERMS
from nanopub.constants import FDO_DATA_REF_HANDLE, FDO_PROFILE_HANDLE, FDO_DATA_REFS_HANDLE
from nanopub.fdo.fdo_nanopub import FdoNanopub, to_hdl_uri
from nanopub.namespaces import HDL, FDOF, NPX
FAKE_HANDLE = "21.T11966/test"
FAKE_LABEL = "Test Object"

@pytest.mark.parametrize("fdo_profile", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_add_fdo_profile(fdo_profile):
    fdo = FdoNanopub(FAKE_HANDLE, FAKE_LABEL)
    uri = to_hdl_uri(fdo_profile)
    fdo.add_fdo_profile(fdo_profile)
    assert (fdo.fdo_uri, DCTERMS.conformsTo, uri) in fdo.assertion
    assert (HDL[FDO_PROFILE_HANDLE], RDFS.label, rdflib.Literal("FdoProfile")) in fdo.pubinfo
    assert_introduces_in_pubinfo(fdo)
