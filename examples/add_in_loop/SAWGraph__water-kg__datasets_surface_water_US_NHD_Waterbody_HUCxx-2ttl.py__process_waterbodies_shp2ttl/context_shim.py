# Context shim (see meta.json): what process_waterbodies_shp2ttl
# (SAWGraph/water-kg@032ec41357, datasets/surface_water/
# US_NHD_Waterbody_HUCxx-2ttl.py) finds around it, so that it executes
# without geopandas, fiona or a shapefile.
#
#   * `_PREFIX` (namespaces.py): the registry of SAWGraph namespaces, a dict
#     from a short name to a Namespace.  The IRIs are reconstructed from the
#     repository's conventions (the nhdplusv2.spatialai.org vocabularies);
#     both representations read the same registry, so their exact spelling
#     does not matter to the comparison.
#   * `load_waterbodies`, `initial_kg`, `build_iris`: the three helpers the
#     script defines above the region, reduced to what the region needs:
#     the shapefile read by geopandas becomes a CSV read by pandas (same
#     columns; NULL fields are None, as the DBF reader gives them), the
#     empty graph binds the registry, the IRIs are minted from the COMID.
#   * `shapely`: a stand-in for the part of shapely the region calls,
#     `wkb.dumps(geom, output_dimension=2)` / `wkb.loads`.  Geometries are
#     WKT strings here; forcing them to 2D drops the Z ordinate.
#
# Identical bindings for both representations.
import re
import types

import pandas as pd
from rdflib import Graph, Namespace

_PREFIX = {
    "hyf": Namespace("https://www.opengis.net/def/schema/hy_features/hyf/"),
    "us_nhdplusv2": Namespace("http://nhdplusv2.spatialai.org/v1/nhdplusv2#"),
    "us_nhdplusv2_data": Namespace("http://nhdplusv2.spatialai.org/v1/nhdplusv2-data#"),
    "us_wbd": Namespace("http://nhdplusv2.spatialai.org/v1/wbd#"),
    "us_wbd_data": Namespace("http://nhdplusv2.spatialai.org/v1/wbd-data#"),
}


def load_waterbodies(vpunum, infile):
    df = pd.read_csv(infile, dtype={"REACHCODE": str, "GNIS_NAME": str})
    return df.astype(object).where(df.notna(), None)


def initial_kg(prefix, vpunum):
    kg = Graph()
    for name, namespace in prefix.items():
        kg.bind(name, namespace)
    return kg


def build_iris(comid, prefix):
    data = prefix["us_nhdplusv2_data"]
    return data[f"d.NHDWaterbody.{comid}"], data[f"d.NHDWaterbody.Geometry.{comid}"]


_Z = re.compile(r"(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) -?\d+(?:\.\d+)?(?=[,)])")


class _Wkb:
    @staticmethod
    def dumps(geometry, output_dimension=3):
        text = str(geometry)
        if output_dimension == 2:
            text = _Z.sub(r"\1 \2", text.replace(" Z ", " "))
        return text.encode("ascii")

    @staticmethod
    def loads(data):
        return data.decode("ascii")


shapely = types.SimpleNamespace(wkb=_Wkb)
