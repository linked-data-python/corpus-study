# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/starrydata.py
# region: _emit_curve (lines 354-473, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV, RDF, XSD
from context_shim import (  # context shim, see meta.json
    parse_curator_timestamp,
    parse_float_array,
    parse_project_names,
    quantity_kind_iri,
    strip_quoted,
    unit_iri,
)
WEBPLOTDIGITIZER_IRI = "https://automeris.io/WebPlotDigitizer"
SCHEMA = Namespace("https://schema.org/")

def _emit_curve(
    g: Graph,
    row: dict[str, str],
    sd: Namespace,
    sdr: Namespace,
    ingestion_iri: URIRef | None,
) -> bool:
    """1 行 (curves.csv) を Graph に追加。

    NOTE: starrydata は 1 つの figure (figure_id) に複数 sample の curve を載せる
    ことがあり、また figure_id 自体も paper を跨いで重複しうる (実測 4,466 件)。
    そのため curve IRI は (SID, figure_id, sample_id) の複合キーで作る:
        sdr:curve/{SID}-{figure_id}-{sample_id}
    starrydata 全件で (SID, figure_id, sample_id) は 100% ユニーク (検証済)。

    設計プラン §4「x/y 配列の表現方針」方針 C:
      - sd:xValuesJSON / sd:yValuesJSON で JSON literal 保持 (xsd:string)
      - sd:xMin / sd:xMax / sd:yMin / sd:yMax / sd:pointCount を集約値として出す
      → 2 次元の局所範囲クエリは集約値だけでは答えられない (既知の限界)
    """
    fig_id = row.get("figure_id", "").strip()
    sample_id = row.get("sample_id", "").strip()
    paper_sid = row.get("SID", "").strip()
    if not fig_id or not sample_id or not paper_sid:
        return False
    curve_key = f"{paper_sid}-{fig_id}-{sample_id}"
    curve = sdr[f"curve/{curve_key}"]
    sample_iri = sdr[f"sample/{paper_sid}-{sample_id}"]

    g.add((curve, RDF.type, sd.Curve))
    g.add((curve, RDF.type, PROV.Entity))
    g.add((curve, DCTERMS.identifier, Literal(curve_key)))
    g.add((curve, sd.rawFigureId, Literal(fig_id)))

    if ingestion_iri is not None:
        g.add((curve, PROV.wasGeneratedBy, ingestion_iri))

    if figure_name := strip_quoted(row.get("figure_name", "")):
        g.add((curve, sd.figureName, Literal(figure_name)))

    g.add((curve, sd.ofSample, sample_iri))

    # Phase 1 string predicates are kept as-is for backward compatibility.
    for col_key, prop in (
        ("prop_x", sd.propertyX),
        ("prop_y", sd.propertyY),
        ("unit_x", sd.unitXString),
        ("unit_y", sd.unitYString),
        ("comments", sd.comments),
    ):
        if value := strip_quoted(row.get(col_key, "")):
            g.add((curve, prop, Literal(value)))

    # Phase 2 #2: additively attach canonical QUDT IRIs when a curated mapping
    # exists. The string predicates above stay; these let AI clients pivot on a
    # stable identifier so "Seebeck coefficient" and "thermopower" unify.
    for col_key, prop in (
        ("prop_x", sd.propertyXQuantity),
        ("prop_y", sd.propertyYQuantity),
    ):
        value = strip_quoted(row.get(col_key, ""))
        if value and (iri := quantity_kind_iri(value)):
            g.add((curve, prop, URIRef(iri)))
    for col_key, prop in (
        ("unit_x", sd.unitX),
        ("unit_y", sd.unitY),
    ):
        value = strip_quoted(row.get(col_key, ""))
        if value and (iri := unit_iri(value)):
            g.add((curve, prop, URIRef(iri)))

    # x / y 配列: JSON literal + 集約値
    x_raw = row.get("x", "")
    y_raw = row.get("y", "")
    xs = parse_float_array(x_raw)
    ys = parse_float_array(y_raw)
    if x_raw:
        g.add((curve, sd.xValuesJSON, Literal(x_raw)))
    if y_raw:
        g.add((curve, sd.yValuesJSON, Literal(y_raw)))
    if xs:
        g.add((curve, sd.xMin, Literal(min(xs), datatype=XSD.double)))
        g.add((curve, sd.xMax, Literal(max(xs), datatype=XSD.double)))
    if ys:
        g.add((curve, sd.yMin, Literal(min(ys), datatype=XSD.double)))
        g.add((curve, sd.yMax, Literal(max(ys), datatype=XSD.double)))
    point_count = min(len(xs), len(ys))
    if point_count:
        g.add((curve, sd.pointCount, Literal(point_count, datatype=XSD.integer)))

    for project in parse_project_names(row.get("project_names", "")):
        g.add((curve, sd.projectName, Literal(project)))

    created = strip_quoted(row.get("created_at", ""))
    if created:
        g.add((curve, DCTERMS.created, Literal(created)))
    if updated := strip_quoted(row.get("updated_at", "")):
        g.add((curve, DCTERMS.modified, Literal(updated)))

    # Phase 2 #6: scientific provenance. Each curve was digitized off a
    # published figure with WebPlotDigitizer; model that as a distinct
    # DigitizationActivity (separate from our IngestionActivity, which only
    # records that *our pipeline* loaded the CSV). A curve is thus
    # prov:wasGeneratedBy two activities — the original digitization and our
    # ingestion — which is valid PROV-O.
    digitization = sdr[f"digitization/{curve_key}"]
    g.add((curve, PROV.wasGeneratedBy, digitization))
    g.add((digitization, RDF.type, sd.DigitizationActivity))
    g.add((digitization, RDF.type, PROV.Activity))
    g.add((digitization, PROV.wasAssociatedWith, URIRef(WEBPLOTDIGITIZER_IRI)))
    if created and (at_time := parse_curator_timestamp(created)):
        g.add((digitization, PROV.atTime, Literal(at_time, datatype=XSD.dateTime)))
    # The WebPlotDigitizer agent description is shared across all curves; the
    # triples are IRI-keyed so Oxigraph set-semantics dedupes them on re-ingest.
    agent = URIRef(WEBPLOTDIGITIZER_IRI)
    g.add((agent, RDF.type, PROV.SoftwareAgent))
    g.add((agent, SCHEMA.name, Literal("WebPlotDigitizer")))
    g.add((agent, SCHEMA.url, URIRef(WEBPLOTDIGITIZER_IRI)))

    return True
