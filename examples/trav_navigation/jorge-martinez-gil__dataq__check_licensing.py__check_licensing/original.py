# Extracted from jorge-martinez-gil/dataq@0808bf5696 : check_licensing.py
# region: check_licensing (lines 31-64, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, Namespace
dcat = Namespace("http://www.w3.org/ns/dcat#")
dcterms = Namespace("http://purl.org/dc/terms/")

def check_licensing(rdf_data: str, rdf_format: str = "turtle") -> float:
    """
    Check the licensing of an RDF data string and return the percentage of datasets 
    (dcat:Dataset) that have a license (dcterms:license).

    Args:
        rdf_data (str): The RDF data string to check.
        rdf_format (str): The format of the RDF data (default: "turtle").

    Returns:
        float: The percentage of datasets that have a license, between 0 and 100.
    """
    graph = Graph()
    try:
        graph.parse(data=rdf_data, format=rdf_format)
    except Exception as e:
        print(f"Error parsing RDF data: {e}")
        return 0.0

    licensed_items = 0
    total_items = 0

    # Iterate through all datasets in the RDF graph
    for subject in graph.subjects(RDF.type, dcat.Dataset):
        total_items += 1
        # Check if the dataset has a license defined using dcterms:license
        if any(graph.triples((subject, dcterms.license, None))):
            licensed_items += 1

    if total_items == 0:
        print("No datasets found in the RDF data.")
        return 0.0

    return (licensed_items / total_items) * 100
