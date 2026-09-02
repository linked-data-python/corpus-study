"""Validation driver for SAWGraph__water-kg__datasets_groundwater_il-isgs_IL_ISGS_Aquifer-AqSystem-2ttl.py__process_aquifers_shp2ttl.

Establishes semantic equivalence of original.py and translated.ldpy.

Both original.py and translated.ldpy `import geopandas as gpd`, which is not
installed in the study venv (see meta.json: excluded, external dependency),
and the region reads four real .shp files that are not part of this corpus
checkout either. run_pair therefore fails at import time on BOTH sides
identically -- this driver documents that, it is not expected to go green.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='process_aquifers_shp2ttl',
    calls=[((), {})],  # unreachable: both sides fail at `import geopandas`
)
