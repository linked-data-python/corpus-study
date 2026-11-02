# Context shim (see meta.json): subset of eclipse-esmf/esmf-sdk-py-aspect-model-loader
# @5ca56eb51c (core/esmf-aspect-meta-model-python/esmf_aspect_meta_model_python),
# so the region executes outside the package (not installed in the study venv).
# Identical bindings for both representations.
#
# SAMM: vocabulary/samm.py `get_urn` and `samm_prefix` verbatim; the attribute
#   constants are those of vocabulary/constants.py (MetaModelElementAttributes)
#   that the region uses.
# Property: base/property.py's abstract class, reduced to a marker (the region
#   only uses it as a return annotation).
# DefaultProperty: impl/default_property.py's constructor signature; it keeps
#   its arguments as attributes (the real one stores them in the same _fields
#   behind properties, and a MetaModelBaseAttributes/Characteristic is opaque
#   to the region).
import rdflib


class Property:
    pass


class DefaultProperty(Property):
    def __init__(self, meta_model_base_attributes, characteristic=None, example_value=None,
                 extends=None, abstract=False, optional=False, not_in_payload=False,
                 payload_name=None):
        self._meta_model_base_attributes = meta_model_base_attributes
        self._characteristic = characteristic
        self._example_value = example_value
        self._extends = extends
        self._is_abstract = abstract
        self._optional = optional
        self._not_in_payload = not_in_payload
        self._payload_name = payload_name


class SAMM:
    samm_prefix = "urn:samm:org.eclipse.esmf.samm:meta-model:"

    characteristic = "characteristic"
    example_value = "exampleValue"
    extends = "extends"
    not_in_payload = "notInPayload"
    optional = "optional"
    payload_name = "payloadName"
    property = "property"

    def __init__(self, meta_model_version: str):
        self.meta_model_version: str = meta_model_version

    def get_urn(self, element_type: str) -> rdflib.URIRef:
        """returns the URN string of the given element type."""
        return rdflib.URIRef(f"{SAMM.samm_prefix}{self.meta_model_version}#{element_type}")
