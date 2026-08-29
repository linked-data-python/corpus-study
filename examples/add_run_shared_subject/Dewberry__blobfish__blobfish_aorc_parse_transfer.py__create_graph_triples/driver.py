"""Validation driver for Dewberry__blobfish__blobfish_aorc_parse_transfer.py__create_graph_triples.

The region builds a graph reached only through `graph_creator.get_graph(...)`
(a side effect, not a returned value), so both files carry an identical
`demo(meta)` harness (see original.py / translated.ldpy and meta.json) that
creates its own GraphCreator/NodeNamer, calls the region, and hands back the
one graph written -- compared by isomorphism.

Two metadata fixtures, differing in every field the region reads (RFC name,
dates, URIs, byte size, docker image, script path), so a mistranslated
predicate or a triple accidentally dropped from a merged `+{ }` run shows up
as a real graph difference rather than an accidental coincidence of values.
"""
from context_shim import CompletedTransferMetadata

from rdfeval.harness import run_pair

META_1 = CompletedTransferMetadata(
    rfc_name="ARKANSAS RED BASIN",
    rfc_alias="AB",
    rfc_catalog_uri="/AORC_ABRFC_4km",
    precip_partition_uri="/ABRFC_precip_partition",
    source_uri="/AORC_APCP_4KM_ABRFC_202001.zip",
    mirror_uri="s3://tempest/mirrors/aorc/precip/AORC_APCP_4KM_ABRFC_202001.zip",
    ref_date="2020-01-01",
    docker_image_url="https://hub.docker.com/layers/njroberts/blobfish-python/1.0.0/images/abc123",
    mirror_script="proj/parse_transfer.py",
    aorc_historic_uri="https://hydrology.nws.noaa.gov/pub/aorc-historic",
    source_last_modified="2020-02-05T12:00:00",
    source_bytes="1048576",
    mirror_last_modified="2020-02-06T08:30:00",
    bucket="tempest",
    mirror_public_uri="https://tempest.s3.amazonaws.com/mirrors/aorc/precip/AORC_APCP_4KM_ABRFC_202001.zip",
    ref_end_date="2020-01-31",
    rfc_office_uri="https://www.weather.gov/abrfc",
)

META_2 = CompletedTransferMetadata(
    rfc_name="NORTHWEST",
    rfc_alias="NW",
    rfc_catalog_uri="/AORC_NWRFC_4km",
    precip_partition_uri="/NWRFC_precip_partition",
    source_uri="/AORC_APCP_4KM_NWRFC_201912.zip",
    mirror_uri="s3://tempest/mirrors/aorc/precip/AORC_APCP_4KM_NWRFC_201912.zip",
    ref_date="2019-12-01",
    docker_image_url="https://hub.docker.com/layers/njroberts/blobfish-python/2.3.1/images/def456",
    mirror_script="proj/parse_transfer_alt.py",
    aorc_historic_uri="https://hydrology.nws.noaa.gov/pub/aorc-historic",
    source_last_modified="2019-12-05T09:15:00",
    source_bytes="2097152",
    mirror_last_modified="2019-12-06T10:45:00",
    bucket="tempest",
    mirror_public_uri="https://tempest.s3.amazonaws.com/mirrors/aorc/precip/AORC_APCP_4KM_NWRFC_201912.zip",
    ref_end_date="2019-12-31",
    rfc_office_uri="https://www.weather.gov/nwrfc",
)

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((META_1,), {}), ((META_2,), {})],
)
