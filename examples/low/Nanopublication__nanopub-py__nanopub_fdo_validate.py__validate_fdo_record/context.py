# Context shim (see meta.json): the bindings the extracted region needs so it
# can execute outside the `nanopub` package.  Used IDENTICALLY by original.py
# and translated.ldpy.  Provenance: Nanopublication/nanopub-py@05022dc4bc.
from dataclasses import dataclass
from typing import List

from rdflib import Graph

# --- nanopub/fdo/validate.py (module level, just above the region) ----------


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]


def _profile_landing_page_uri_to_api_url(uri: str) -> str:
    """
    Convert an FdoProfile landing page URI into a handle API URI unless it is already an API URI.

    Examples:
    - https://hdl.handle.net/21.T11966/996c38676da9ee56f8ab
      -> https://hdl.handle.net/api/handles/21.T11966/996c38676da9ee56f8ab

    - https://hdl.handle.net/api/handles/21.T11966/996c38676da9ee56f8ab
      -> returns as is
    """
    if uri.startswith("https://hdl.handle.net/api/handles/"):
        return uri  # Already API URL

    if uri.startswith("https://doi.org/"):
        handle = uri.replace("https://doi.org/", "")
        return f"https://hdl.handle.net/api/handles/{handle}"

    parts = uri.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid handle URI: {uri}")
    handle = "/".join(parts[-2:])
    api_url = f"https://hdl.handle.net/api/handles/{handle}"
    return api_url


# --- nanopub/definitions.py -------------------------------------------------

DEFAULT_HTTP_TIMEOUT = (5, 30)


# --- annotation-only names --------------------------------------------------
# FdoRecord / FdoNanopub appear only in the signature annotations of the
# region; the driver passes duck-typed doubles.  Stand-ins keep the module
# importable without dragging in the whole nanopub package.


class FdoRecord:  # nanopub/fdo/fdo_record.py
    pass


class FdoNanopub:  # nanopub/fdo/fdo_nanopub.py
    pass


# --- test doubles for the un-exercised branches -----------------------------
# `requests`, `pyshacl`, and the nanopub network helpers are not available in
# the evaluation environment.  The driver only exercises the `profile_np is
# not None` branch, so these are never called; they raise if they ever are.


def _unavailable(name):
    def _stub(*args, **kwargs):
        raise RuntimeError(f"{name} is not available in the evaluation environment")
    return _stub


class _Requests:
    get = staticmethod(_unavailable("requests.get"))


requests = _Requests()

resolve_in_nanopub_network = _unavailable("resolve_in_nanopub_network")
convert_jsonschema_to_shacl = _unavailable("convert_jsonschema_to_shacl")
looks_like_handle = _unavailable("looks_like_handle")
fix_numeric_shacl_constraints = _unavailable("fix_numeric_shacl_constraints")


# --- pyshacl stand-in -------------------------------------------------------
# pySHACL is not installed here.  The region's own RDF behaviour is limited to
# reading sh:resultMessage out of the report graph, so the double returns a
# fixed, realistic SHACL validation report; both representations consume the
# very same object.

_REPORT = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

[] a sh:ValidationReport ;
   sh:conforms false ;
   sh:result [ a sh:ValidationResult ;
               sh:focusNode ex:fdo1 ;
               sh:resultPath ex:hasProfile ;
               sh:resultSeverity sh:Violation ;
               sh:resultMessage "Value does not have class ex:Profile" ],
             [ a sh:ValidationResult ;
               sh:focusNode ex:fdo1 ;
               sh:resultPath ex:label ;
               sh:resultSeverity sh:Violation ;
               sh:resultMessage "Less than 1 values on ex:fdo1->ex:label" ] .
"""


def _pyshacl_validate(data_graph, shacl_graph=None, **kwargs):
    report = Graph().parse(data=_REPORT, format="turtle")
    return False, report, "Validation Report\nConforms: False\n"
