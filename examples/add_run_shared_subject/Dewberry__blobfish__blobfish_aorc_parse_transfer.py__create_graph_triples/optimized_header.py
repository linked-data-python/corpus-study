# Extracted from Dewberry/blobfish@db89f34228 : blobfish/aorc/parse_transfer.py
# region: create_graph_triples (lines 175-270, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import RDF, OWL, XSD, DCAT, DCTERMS, PROV, Literal, URIRef, BNode
from context_shim import AORC, AORCFilter, GraphCreator, NodeNamer, CompletedTransferMetadata

def create_graph_triples(
    meta: CompletedTransferMetadata, graph_creator: GraphCreator, node_namer: NodeNamer, filter: AORCFilter | None
) -> None:
    # Apply filter to get distinct graphs depending on metadata properties
    filter_value = None
    if filter:
        if filter.name == "YEAR":
            filter_value = meta.ref_date[:4]
        elif filter.name == "RFC":
            filter_value = meta.rfc_alias
    g = graph_creator.get_graph(filter_value)

    source_dataset_node = BNode(node_namer.name_source_ds(meta))
    source_dataset_period_of_time_node = BNode(node_namer.name_ds_period(meta))
    precip_partition_uri = URIRef(meta.aorc_historic_uri + meta.rfc_catalog_uri + meta.precip_partition_uri)
    source_distribution_uri = precip_partition_uri + meta.source_uri
    mirror_dataset_uri = URIRef(meta.mirror_uri)
    mirror_distribution_uri = URIRef(meta.mirror_public_uri)
    script_node = BNode(meta.mirror_script)
    docker_image_uri = URIRef(meta.docker_image_url)
    transfer_job_node = BNode(node_namer.name_transfer(meta))
    rfc_office_uri = URIRef(meta.rfc_office_uri)
    g += [
        # Create source dataset instance, properties
        (source_dataset_node, RDF.type, AORC.SourceDataset),
        (source_dataset_node, DCTERMS.temporal, source_dataset_period_of_time_node),
        (source_dataset_node, DCTERMS.accrualPeriodicity, URIRef("http://purl.org/cld/freq/monthly")),
        # Associate distribution with dataset
        (source_dataset_node, DCAT.distribution, source_distribution_uri),
        (source_dataset_period_of_time_node, RDF.type, DCTERMS.PeriodOfTime),
        (source_dataset_period_of_time_node, DCAT.startDate, Literal(meta.ref_date, datatype=XSD.date)),
        (source_dataset_period_of_time_node, DCAT.endDate, Literal(meta.ref_end_date, datatype=XSD.date)),
        # Create source dataset distribution instance, properties
        (source_distribution_uri, RDF.type, AORC.SourceDistribution),
        (source_distribution_uri, DCAT.byteSize, Literal(meta.source_bytes, datatype=XSD.positiveInteger)),
        (source_distribution_uri, DCTERMS.modified, Literal(meta.source_last_modified, datatype=XSD.dateTime)),
        (source_distribution_uri, DCAT.compressFormat,
         URIRef("https://www.iana.org/assignments/media-types/application/zip")),
        (source_distribution_uri, DCAT.packageFormat,
         URIRef("https://publications.europa.eu/resource/authority/file-type/NETCDF")),
        # Create mirror dataset instance, properties
        (mirror_dataset_uri, RDF.type, AORC.MirrorDataset),
        (mirror_dataset_uri, DCTERMS.created, Literal(meta.mirror_last_modified, datatype=XSD.dateTime)),
        (mirror_dataset_uri, OWL.Annotation, Literal(
            "Access is restricted based on users credentials for AWS bucket holding data", datatype=XSD.string
        )),
        # Associate mirror dataset with source dataset
        (mirror_dataset_uri, AORC.hasSourceDataset, source_dataset_node),
        # Associate mirror distribution with mirror dataset
        (mirror_dataset_uri, DCAT.distribution, mirror_distribution_uri),
        # Create mirror distribution instance, properties
        (mirror_distribution_uri, RDF.type, AORC.MirrorDistribution),
        # Create transfer script instance
        (script_node, RDF.type, AORC.TransferScript),
        (script_node, DCTERMS.identifier, Literal(meta.mirror_script)),
        # Create docker image instance, properties
        (docker_image_uri, RDF.type, AORC.DockerImage),
        (docker_image_uri, AORC.hasTransferScript, script_node),
        # Create transfer job activity instance, properties
        (transfer_job_node, RDF.type, AORC.TransferJob),
        (transfer_job_node, AORC.transferred, mirror_dataset_uri),
        (transfer_job_node, PROV.used, source_dataset_node),
        (transfer_job_node, PROV.wasStartedBy, script_node),
        # Create RFC office instance
        (rfc_office_uri, RDF.type, AORC.RFC),
        (rfc_office_uri, AORC.hasRFCName, Literal(meta.rfc_name, datatype=XSD.string)),
        (rfc_office_uri, AORC.hasRFCAlias, Literal(meta.rfc_alias, datatype=XSD.string)),
        # Create precip partition catalog instance, properties
        (precip_partition_uri, RDF.type, AORC.PrecipPartition),
        (precip_partition_uri, DCAT.keyword, Literal("precipitation", datatype=XSD.string)),
        (precip_partition_uri, AORC.hasRFC, rfc_office_uri),
        # Associate precip partition catalog with source dataset it holds
        (precip_partition_uri, DCAT.dataset, source_dataset_node),
    ]


# Demo harness (identical on both sides, see meta.json): create_graph_triples
# returns None and writes through graph_creator.get_graph(...), not through a
# plain Graph argument the driver could compare -- GraphCreator has no
# __eq__, so comparing the argument itself would compare object identity and
# always fail.  This wraps the call and hands back the one graph it wrote to,
# compared by isomorphism as usual.
def demo(meta):
    graph_creator = GraphCreator({"dcat": DCAT, "prov": PROV, "dct": DCTERMS, "aorc": AORC})
    node_namer = NodeNamer()
    create_graph_triples(meta, graph_creator, node_namer, None)
    return graph_creator.default_graph
