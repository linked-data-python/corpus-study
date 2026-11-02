"""Validation driver for SAWGraph__water-kg__datasets_surface_water_US_NHD_Waterbody_HUCxx-2ttl.py__process_waterbodies_shp2ttl.

The region triplifies water bodies and writes them to a .ttl file, returning
nothing: what it shows is the FILE (compared as an RDF graph by the harness),
besides the two log records of the 2D pass and its own.  The paths are fixed
relative paths (the check runs in the example directory): the input is
`waterbodies.csv` (the stand-in of context_shim.py for the shapefile) and the
output `waterbodies_0101.ttl`, removed by the harness after each side.

waterbodies.csv holds six bodies that span the branches of the region:
  101 Estuary, 102 LakePond ('lake'), 103 Reservoir, 104 SwampMarsh (the
  `else`: HY_WaterBody) -- the four types of the if/elif chain; 104 and 105
  have no GNIS_NAME (None: no sdo:name); 105 has no REACHCODE (None: no
  containingHUC); 106 has a 4-character REACHCODE ('0108', the [:8] slice
  keeps it whole) and a 2D geometry already ('Ice Mass': HY_WaterBody).
The others have a 3D polygon: forcing it to 2D must show in the WKT literal.
A second call reads a file that does not exist and raises the same error
on both sides, before anything is written.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='process_waterbodies_shp2ttl',
    calls=[
        (("0101", "waterbodies.csv", "waterbodies_0101.ttl"), {}),
        (("0101", "missing.csv", "waterbodies_missing.ttl"), {}),
    ],
)
