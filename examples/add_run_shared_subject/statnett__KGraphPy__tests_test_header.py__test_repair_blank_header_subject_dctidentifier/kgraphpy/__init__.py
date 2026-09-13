# Context shim (see meta.json): subset of kgraphpy/__init__.py from
# statnett/KGraphPy@38859be62fdc2fd048e3ad1651bc16f0dcabaf75, so the region
# executes outside the package. Identical bindings for both representations.
# Only the piece the test exercises is kept: setting the default metadata
# object types, which the real __init__.py does at import time.
from kgraphpy.header import CIMMetadataHeader
from kgraphpy.namespaces import MD
from rdflib.namespace import DCAT

CIMMetadataHeader.DEFAULT_METADATA_OBJECTS = {
    MD.FullModel,
    DCAT.Dataset,
}
