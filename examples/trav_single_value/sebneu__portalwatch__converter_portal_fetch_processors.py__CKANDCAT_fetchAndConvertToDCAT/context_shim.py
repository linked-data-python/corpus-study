# Context shim (see meta.json): the parts of sebneu/portalwatch that
# CKANDCAT.fetchAndConvertToDCAT depends on but that are not part of the
# extracted region, transcribed from
# sebneu/portalwatch@a514eba7bfb21c62ac75ad4745a28435475021d5 so the region
# executes outside the package (requests/ckanapi/geomet/rfc3987/dateutil are
# not in the study venv, and the venv is pinned).
# Identical bindings for both representations.
#
# What is reproduced verbatim: `namespaces['hydra']` and `DCAT`, both from
# converter/dataset_converter.py -- the two namespace bindings the region
# actually reads. The other ten keys of the real `namespaces` dict (dct,
# adms, vcard, foaf, schema, time, skos, locn, gsp, owl) are never touched by
# this region and are left out rather than transcribed unused.
#
# What is a stand-in and why: `no_ssl_verification` (utils/ssl_ignore.py) is
# a no-op here -- driver.py's fixtures are local files, never a real HTTPS
# request, so there is nothing for it to make insecure. `convert_socrata`,
# `graph_from_opendatasoft`, `graph_from_data_gouv_fr` and `CKANConverter`
# are imported by the region's module but never called by
# fetchAndConvertToDCAT (that method only ever runs the CKAN-via-RDF-endpoint
# path); each stand-in raises rather than answers, so a future fixture that
# did reach one would fail loudly instead of diverging silently.
from __future__ import annotations

import contextlib

from rdflib import Namespace

DCAT = Namespace("http://www.w3.org/ns/dcat#")
HYDRA = Namespace("http://www.w3.org/ns/hydra/core#")
namespaces = {"hydra": HYDRA}


@contextlib.contextmanager
def no_ssl_verification():
    yield


def convert_socrata(*args, **kwargs):
    raise NotImplementedError(
        "not reached by driver.py's fixtures: fetchAndConvertToDCAT is the "
        "CKAN-via-RDF-endpoint path and never calls the Socrata converter; "
        "see the shim header")


def graph_from_opendatasoft(*args, **kwargs):
    raise NotImplementedError(
        "not reached by driver.py's fixtures: fetchAndConvertToDCAT never "
        "calls the OpenDataSoft converter; see the shim header")


def graph_from_data_gouv_fr(*args, **kwargs):
    raise NotImplementedError(
        "not reached by driver.py's fixtures: fetchAndConvertToDCAT never "
        "calls the data.gouv.fr converter; see the shim header")


class CKANConverter:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "not reached by driver.py's fixtures: fetchAndConvertToDCAT "
            "(the RDF-endpoint CKAN+DCAT path) never instantiates the "
            "dataset-dict CKANConverter; see the shim header")
