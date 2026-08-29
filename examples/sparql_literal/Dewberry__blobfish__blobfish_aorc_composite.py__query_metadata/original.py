# Extracted from Dewberry/blobfish@db89f34228 : blobfish/aorc/composite.py
# region: query_metadata (lines 108-135, stratum sparql_literal)
# licence of the source repository: see meta.json
import logging
from collections.abc import Generator
from rdflib import XSD, DCAT, DCTERMS, PROV, Graph, Literal
from typing import cast
from .const import RFC_INFO_LIST
from ..pyrdf import AORC

def query_metadata(g: Graph) -> Generator[DatedPaths, None, None]:
    # Get unique start date and end date pairs which denote distinct periods of temporal coverage for datasets
    time_coverage_query = """
    SELECT  DISTINCT ?sd ?ed
    WHERE   {
        ?s dcat:startDate ?sd .
        ?s dcat:endDate ?ed
    }
    """
    time_results = g.query(time_coverage_query, initNs={"dcat": DCAT})
    for result in time_results:
        start_date, end_date = cast(list, result)
        new_query = (
            """
        SELECT  ?mda
        WHERE   {\n"""
            + f"""\t\t"{start_date}"^^xsd:date ^dcat:startDate/^dct:temporal/^aorc:hasSourceDataset ?mda ."""
            + """\n\t}"""
        )
        source_results = g.query(new_query, initNs={"dcat": DCAT, "xsd": XSD, "dct": DCTERMS, "aorc": AORC})
        formatted_start_date = format_xsd_date(start_date)
        formatted_end_date = format_xsd_date(end_date)
        s3_paths = [str(cast(list, result)[0]) for result in source_results]
        # Check to make sure the length of the s3 paths is the same as the length of the list of RFC offices
        if len(RFC_INFO_LIST) == len(s3_paths):
            logging.error(f"Expected {len(RFC_INFO_LIST)} to match RFC office number, got {len(s3_paths)}")
            # raise AttributeError
        yield DatedPaths(formatted_start_date, formatted_end_date, s3_paths)
