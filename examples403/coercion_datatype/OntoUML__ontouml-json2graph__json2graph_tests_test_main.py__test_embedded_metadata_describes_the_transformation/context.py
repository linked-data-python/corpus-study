# Context shim (see meta.json): the two sibling-module imports of
# json2graph/tests/test_main.py that this region's context lines carry
# verbatim as relative imports --
#   from ..modules.content_identity import create_content_uuid, resolve_base_uri
#   from ..modules.metadata import METADATA, _read_source_project_version
# -- which raise `ImportError: attempted relative import with no known
# parent package` outside the ontouml-json2graph package.
#
# content_identity.create_content_uuid / normalize_base_uri / resolve_base_uri
# are pure, standalone functions (hashlib/json/uuid/urllib.parse only, no
# other project modules) -- reproduced verbatim from
# json2graph/modules/content_identity.py @982f12b9c4.
#
# metadata.METADATA/_read_source_project_version pull in importlib.metadata,
# a pyproject.toml lookup and the project's own logger. Reproducing that
# chain would not change whether this region can run to completion: the
# actual blocker is four sibling test helpers this shim does NOT attempt to
# fake (write_cardinality_project, run_metadata_cli, get_output_artifact,
# get_recorded_configuration -- see meta.json, classification: excluded).
# METADATA is therefore a representative stand-in carrying only the two
# fields the region reads (Name, Version); _read_source_project_version is a
# stub matching its documented return type.
#
# Identical bindings for both representations.
import hashlib
import json
import uuid
from urllib.parse import urlsplit


def canonicalize_json(json_data):
    return json.dumps(
        json_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


JSON2GRAPH_NAMESPACE_UUID = uuid.UUID("3f6e741a-4a05-5962-83d0-343fc9d7dc22")


def create_content_uuid(json_data):
    canonical_json = canonicalize_json(json_data)
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return uuid.uuid5(JSON2GRAPH_NAMESPACE_UUID, digest)


def normalize_base_uri(base_uri):
    if not isinstance(base_uri, str) or not base_uri or any(c.isspace() for c in base_uri):
        raise ValueError("Base URI must be a non-empty absolute URI without whitespace.")
    parsed_uri = urlsplit(base_uri)
    if not parsed_uri.scheme:
        raise ValueError("Base URI must be an absolute URI with a scheme.")
    if parsed_uri.scheme.lower() in ("http", "https") and not parsed_uri.netloc:
        raise ValueError("HTTP(S) base URI must include a host.")
    if base_uri.endswith(("#", "/")):
        return base_uri
    return f"{base_uri}#"


def resolve_base_uri(json_data, base_uri=None, append_content_hash=False):
    content_uuid = create_content_uuid(json_data)
    if base_uri is None:
        return f"urn:uuid:{content_uuid}#"
    normalized_base_uri = normalize_base_uri(base_uri)
    if not append_content_hash:
        return normalized_base_uri
    parsed_uri = urlsplit(base_uri)
    if parsed_uri.query or parsed_uri.fragment:
        raise ValueError("A base URI with a content ID cannot contain a query or non-empty fragment.")
    parent_uri = base_uri.rstrip("/#")
    return f"{parent_uri}/{content_uuid}#"


METADATA = {"Name": "ontouml-json2graph", "Version": "X.X.X"}


def _read_source_project_version():
    return None
