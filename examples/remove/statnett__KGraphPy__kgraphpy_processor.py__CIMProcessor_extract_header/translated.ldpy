# Extracted from statnett/KGraphPy@38859be62f : kgraphpy/processor.py
# region: CIMProcessor.extract_header (lines 77-89, stratum remove)
# licence of the source repository: see meta.json
from kgraphpy.header import create_header_attribute, CIMMetadataHeader
logger = logging.getLogger('cimxml_logger')

def extract_header(self) -> None:
    """Move header triples from graph to the metadata_header attribute."""
    if self.graph.metadata_header:
        logger.error("Metadata header already exist. Use .replace_header instead.")
        return

    header = create_header_attribute(self.graph)
    self.graph.metadata_header = header
    self.graph.remove((header.subject, None, None))

    # Remove blank nodes that belong to the header
    for subject_node in header.reachable_nodes:
        self.graph.remove((subject_node, None, None))
