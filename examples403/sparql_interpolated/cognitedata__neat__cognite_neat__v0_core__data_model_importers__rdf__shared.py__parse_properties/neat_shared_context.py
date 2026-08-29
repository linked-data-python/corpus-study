# Context shim (see meta.json): subset of the free variables `parse_properties`
# (cognite/neat/_v0/core/_data_model/importers/_rdf/_shared.py) uses without
# importing -- its three module-level siblings `convert_rdflib_content`,
# `sanitize_entity`, `handle_meta` in the same file, and their own transitive
# dependencies -- reproduced from cognitedata/neat@4042d3e96d so the region
# executes outside the package. Identical bindings for both representations.
#
# `convert_rdflib_content`, `sanitize_entity`, `uri_to_entity_components` and
# `remove_namespace_from_uri` are copied verbatim (trimmed of the
# `validation="full"` pydantic-URL-validation branch of
# `remove_namespace_from_uri`, which `parse_properties` never reaches -- it
# always calls with the default `validation="prefix"`).
#
# `IssueList`, `NeatValueError`, `ResourceRedefinedWarning` and
# `ResourceRetrievalWarning` are minimal re-declarations with the same fields
# and construction signature as the real dataclasses in
# `cognite/neat/_v0/core/_issues/*` -- the real ones pull in pandas and the
# Cognite Python SDK transitively (through `_issues/_base.py`'s own imports)
# well beyond what parsing a plain `dict`/`str` field needs here.
#
# `ConceptEntity` is a stub, never instantiated by this region's fixture: its
# real constructor path is `convert_rdflib_content(..., uri_handling=
# "as-concept-entity")`, taken only when `uri_to_entity_components` finds a
# URI under one of the real, deployed Cognite namespaces (see
# `cognite_prefixes` below) -- fixture.ttl deliberately uses plain
# `http://example.org/` URIs instead, so `uri_to_entity_components` always
# returns None and this branch is unreachable either side.
from dataclasses import dataclass
from urllib.parse import quote

from rdflib import Literal as RdfLiteral
from rdflib import Namespace, URIRef


# --- cognite/neat/_v0/core/_data_model/models/entities/_constants.py -------

class _UnknownType:
    def __str__(self) -> str:
        return "#N/A"

    def __hash__(self) -> int:
        return hash(str(self))


Unknown = _UnknownType()


# --- cognite/neat/_v0/core/_data_model/models/entities/_single_value.py ----

class ConceptEntity:
    """Stub -- see module docstring: unreachable on this region's fixture."""

    def __init__(self, *, prefix, suffix, version=None):
        self.prefix, self.suffix, self.version = prefix, suffix, version

    def __str__(self) -> str:
        return f"{self.prefix}:{self.suffix}" + (f"(version={self.version})" if self.version else "")


# --- cognite/neat/_v0/core/_constants.py ------------------------------------

CDF_NAMESPACE = Namespace("https://cognitedata.com/")

# The real COGNITE_SPACES frozenset, verbatim (cognite/neat/_v0/core/_constants.py):
COGNITE_SPACES = frozenset(
    {
        "cdf_cdm",
        "cdf_idm",
        "cdf_360_image_schema",
        "cdf_3d_schema",
        "cdf_apm",
        "cdf_apps_shared",
        "cdf_cdm_3d",
        "cdf_cdm_units",
        "cdf_classic",
        "cdf_core",
        "cdf_extraction_extensions",
        "cdf_industrial_canvas",
        "cdf_infield",
        "cdf_time_series_data",
        "cdf_units",
    }
)


def cognite_prefixes() -> dict[str, Namespace]:
    """Returns the Cognite prefixes and namespaces."""
    return {space: Namespace(CDF_NAMESPACE[space] + "/") for space in COGNITE_SPACES}


# --- cognite/neat/_v0/core/_utils/rdf_.py -----------------------------------

def remove_namespace_from_uri(URI, *, special_separator: str = "#_", validation: str = "prefix") -> str:
    """Removes namespace from URI (validation="prefix" path only -- see module docstring)."""
    u = str(URI)
    if u.lower().startswith("http"):
        return u.split(special_separator if special_separator in u else "#" if "#" in u else "/")[-1]
    return u


def uri_to_entity_components(uri, prefixes: dict[str, Namespace]):
    """Converts a URI to its components: space, data_model_id, version, and entity_id."""
    for prefix, namespace in prefixes.items():
        if uri.startswith(namespace):
            remainder = str(uri)[len(str(namespace)):]
            if (components := remainder.split("/")) and len(components) == 3 and all(components):
                return prefix, components[0], components[1], components[2]
    return None


# --- cognite/neat/_v0/core/_data_model/importers/_rdf/_shared.py -----------
# (parse_properties's own module-level siblings)

def convert_rdflib_content(content, uri_handling: str = "skip", prefixes: dict[str, Namespace] | None = None):
    """Converts rdflib content to a more Python-friendly format."""
    if isinstance(content, RdfLiteral):
        return content.toPython()
    elif isinstance(content, URIRef):
        if uri_handling == "remove-namespace":
            return remove_namespace_from_uri(content)
        elif uri_handling == "as-concept-entity":
            if components := uri_to_entity_components(content, prefixes or {}):
                return ConceptEntity(prefix=components[0], suffix=components[3], version=components[2])
            return convert_rdflib_content(content, uri_handling="remove-namespace", prefixes=prefixes)
        else:
            return content.toPython()
    elif isinstance(content, dict):
        return {key: convert_rdflib_content(value, uri_handling, prefixes) for key, value in content.items()}
    elif isinstance(content, list):
        return [convert_rdflib_content(item, uri_handling, prefixes) for item in content]
    else:
        return content


def sanitize_entity(entity, safe: str = "") -> str:
    """Sanitize an entity to ensure it yields entity form that will pass downstream validation."""
    if isinstance(entity, str):
        return quote(entity, safe=safe)
    elif isinstance(entity, ConceptEntity):
        return str(entity)
    else:
        raise ValueError(f"Invalid entity type: {type(entity)}. Expected str, ConceptEntity.")


def handle_meta(resource_type, resources, resource_id, res, feature, issue_list) -> None:
    if not resources[resource_id][feature] and res[feature]:
        resources[resource_id][feature] = res[feature]

    current_value = resources[resource_id][feature]
    new_value = res[feature]

    if not current_value and new_value:
        resources[resource_id][feature] = new_value
    elif current_value and new_value and current_value != new_value:
        issue_list.append(
            ResourceRedefinedWarning(
                identifier=resource_id,
                resource_type=resource_type,
                feature=feature,
                current_value=current_value,
                new_value=new_value,
            )
        )


# --- cognite/neat/_v0/core/_issues/_base.py ---------------------------------

class IssueList(list):
    """This is a generic list of NeatIssues."""

    def __init__(self, issues=None, title: str | None = None, action: str | None = None, hint: str | None = None):
        super().__init__(issues or [])
        self.title = title
        self.action = action
        self.hint = hint


# --- cognite/neat/_v0/core/_issues/errors/_general.py -----------------------

@dataclass(eq=True)
class NeatValueError(ValueError):
    raw_message: str


# --- cognite/neat/_v0/core/_issues/warnings/_resources.py -------------------

@dataclass(eq=True)
class ResourceRetrievalWarning:
    resources: object
    resource_type: str
    error: str | None = None


@dataclass(eq=True)
class ResourceRedefinedWarning:
    identifier: object
    resource_type: str
    feature: str
    current_value: object
    new_value: object
