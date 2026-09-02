# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_fdo_nanopub.py
# region: test_add_fdo_profile (lines 82-89, stratum ns_import_project)
# licence of the source repository: see meta.json
#
# Executability restoration (AGENT_BATCH "163 regions" case, see meta.json):
# `assert_introduces_in_pubinfo` is a module-level helper the region's own
# body calls (test_fdo_nanopub.py, defined around line 21) that the
# extraction did not capture; restored verbatim below (identical on both
# sides). `nanopub` is a real PyPI dependency (pip index versions nanopub:
# 2.2.2 available; every transitive requirement was already satisfied in
# the venv, and installing it left rdflib pinned at 7.2.1 -- see meta.json),
# installed for this pair. No network call happens: `FdoNanopub(...)` called
# with no `source_uri`/`conf` builds its graphs purely in-memory (verified
# directly before writing this pair).
import pytest
import rdflib
from rdflib import RDF, RDFS, DCTERMS
from nanopub.constants import FDO_DATA_REF_HANDLE, FDO_PROFILE_HANDLE, FDO_DATA_REFS_HANDLE
from nanopub.fdo.fdo_nanopub import FdoNanopub, to_hdl_uri
from nanopub.namespaces import HDL, FDOF, NPX
FAKE_HANDLE = "21.T11966/test"
FAKE_LABEL = "Test Object"

def assert_introduces_in_pubinfo(fdo: FdoNanopub):
    assert (fdo.metadata.np_uri, NPX.introduces, fdo.fdo_uri) in fdo.pubinfo


@pytest.mark.parametrize("fdo_profile", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_add_fdo_profile(fdo_profile):
    fdo = FdoNanopub(FAKE_HANDLE, FAKE_LABEL)
    uri = to_hdl_uri(fdo_profile)
    fdo.add_fdo_profile(fdo_profile)
    assert (fdo.fdo_uri, DCTERMS.conformsTo, uri) in fdo.assertion
    assert (HDL[FDO_PROFILE_HANDLE], RDFS.label, rdflib.Literal("FdoProfile")) in fdo.pubinfo
    assert_introduces_in_pubinfo(fdo)
