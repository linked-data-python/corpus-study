# Extracted from kumagallium/asterism@f0977d4d3a : ingest/tests/test_samples_curves.py
# region: test_curves_aggregates (lines 319-338, stratum trav_one_step)
# licence of the source repository: see meta.json
from pathlib import Path
import pytest
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV, RDF, XSD
from asterism.starrydata import (
    DEFAULT_ONTOLOGY,
    DEFAULT_RESOURCE,
    IngestConfig,
    ingest_curves,
    ingest_samples,
    parse_float_array,
    parse_sample_info,
)
SD = Namespace(DEFAULT_ONTOLOGY)

def test_curves_aggregates(curves_csv: Path, tmp_path: Path) -> None:
    """設計プラン §4 方針 C: x/y 集約値 (Min/Max/PointCount) を出す"""
    out = tmp_path / "curves.ttl"
    ingest_curves(curves_csv, out, IngestConfig(emit_prov=False))
    g = _load(out)
    c79 = URIRef(DEFAULT_RESOURCE + "curve/6-79-113")  # SID=6 / figure=79 / sample=113
    x_min = list(g.objects(c79, SD.xMin))
    x_max = list(g.objects(c79, SD.xMax))
    y_min = list(g.objects(c79, SD.yMin))
    y_max = list(g.objects(c79, SD.yMax))
    point_count = list(g.objects(c79, SD.pointCount))
    assert len(x_min) == 1 and float(x_min[0]) == 300.0
    assert len(x_max) == 1 and float(x_max[0]) == 650.0
    # Y min/max: with negatives, min = -0.0004, max = -0.0001
    assert len(y_min) == 1 and float(y_min[0]) == pytest.approx(-0.0004)
    assert len(y_max) == 1 and float(y_max[0]) == pytest.approx(-0.0001)
    assert len(point_count) == 1 and int(point_count[0]) == 5
    # xsd:double / xsd:integer のデータ型確認
    assert x_min[0].datatype == XSD.double
    assert point_count[0].datatype == XSD.integer
