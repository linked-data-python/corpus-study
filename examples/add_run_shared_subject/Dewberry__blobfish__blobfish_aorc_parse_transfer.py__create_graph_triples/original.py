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

    # Create source dataset instance, properties
    source_dataset_node = BNode(node_namer.name_source_ds(meta))
    g.add((source_dataset_node, RDF.type, AORC.SourceDataset))
    source_dataset_period_of_time_node = BNode(node_namer.name_ds_period(meta))
    g.add((source_dataset_period_of_time_node, RDF.type, DCTERMS.PeriodOfTime))
    g.add((source_dataset_node, DCTERMS.temporal, source_dataset_period_of_time_node))
    source_dataset_period_start = Literal(meta.ref_date, datatype=XSD.date)
    g.add((source_dataset_period_of_time_node, DCAT.startDate, source_dataset_period_start))
    source_dataset_period_end = Literal(meta.ref_end_date, datatype=XSD.date)
    g.add((source_dataset_period_of_time_node, DCAT.endDate, source_dataset_period_end))

    # Create source dataset distribution instance, properties
    source_distribution_uri = URIRef(
        "".join([meta.aorc_historic_uri, meta.rfc_catalog_uri, meta.precip_partition_uri, meta.source_uri])
    )
    g.add((source_distribution_uri, RDF.type, AORC.SourceDistribution))
    source_distribution_byte_size = Literal(meta.source_bytes, datatype=XSD.positiveInteger)
    g.add((source_distribution_uri, DCAT.byteSize, source_distribution_byte_size))
    source_last_modified = Literal(meta.source_last_modified, datatype=XSD.dateTime)
    g.add((source_distribution_uri, DCTERMS.modified, source_last_modified))
    zip_compression = URIRef("https://www.iana.org/assignments/media-types/application/zip")
    g.add((source_distribution_uri, DCAT.compressFormat, zip_compression))
    netcdf_format = URIRef("https://publications.europa.eu/resource/authority/file-type/NETCDF")
    g.add((source_distribution_uri, DCAT.packageFormat, netcdf_format))
    monthly_frequency = URIRef("http://purl.org/cld/freq/monthly")
    g.add((source_dataset_node, DCTERMS.accrualPeriodicity, monthly_frequency))

    # Associate distribution with dataset
    g.add((source_dataset_node, DCAT.distribution, source_distribution_uri))

    # Create mirror dataset instance, properties
    mirror_dataset_uri = URIRef(meta.mirror_uri)
    g.add((mirror_dataset_uri, RDF.type, AORC.MirrorDataset))
    mirror_last_modified = Literal(meta.mirror_last_modified, datatype=XSD.dateTime)
    g.add((mirror_dataset_uri, DCTERMS.created, mirror_last_modified))
    access_description = Literal(
        "Access is restricted based on users credentials for AWS bucket holding data", datatype=XSD.string
    )
    g.add((mirror_dataset_uri, OWL.Annotation, access_description))

    # Associate mirror dataset with source dataset
    g.add((mirror_dataset_uri, AORC.hasSourceDataset, source_dataset_node))

    # Create mirror distribution instance, properties
    mirror_distribution_uri = URIRef(meta.mirror_public_uri)
    g.add((mirror_distribution_uri, RDF.type, AORC.MirrorDistribution))

    # Associate mirror distribution with mirror dataset
    g.add((mirror_dataset_uri, DCAT.distribution, mirror_distribution_uri))

    # Create transfer script instance
    script_node = BNode(meta.mirror_script)
    g.add((script_node, RDF.type, AORC.TransferScript))
    g.add((script_node, DCTERMS.identifier, Literal(meta.mirror_script)))

    # Create docker image instance, properties
    docker_image_uri = URIRef(meta.docker_image_url)
    g.add((docker_image_uri, RDF.type, AORC.DockerImage))
    g.add((docker_image_uri, AORC.hasTransferScript, script_node))

    # Create transfer job activity instance, properties
    transfer_job_node = BNode(node_namer.name_transfer(meta))
    g.add((transfer_job_node, RDF.type, AORC.TransferJob))
    g.add((transfer_job_node, AORC.transferred, mirror_dataset_uri))
    g.add((transfer_job_node, PROV.used, source_dataset_node))
    g.add((transfer_job_node, PROV.wasStartedBy, script_node))

    # Create RFC office instance
    rfc_office_uri = URIRef(meta.rfc_office_uri)
    g.add((rfc_office_uri, RDF.type, AORC.RFC))
    rfc_office_title = Literal(meta.rfc_name, datatype=XSD.string)
    g.add((rfc_office_uri, AORC.hasRFCName, rfc_office_title))
    rfc_office_alias = Literal(meta.rfc_alias, datatype=XSD.string)
    g.add((rfc_office_uri, AORC.hasRFCAlias, rfc_office_alias))

    # Create precip partition catalog instance, properties
    precip_partition_uri = URIRef("".join([meta.aorc_historic_uri, meta.rfc_catalog_uri, meta.precip_partition_uri]))
    precip_keyword_uri = Literal("precipitation", datatype=XSD.string)
    g.add((precip_partition_uri, RDF.type, AORC.PrecipPartition))
    g.add((precip_partition_uri, DCAT.keyword, precip_keyword_uri))
    g.add((precip_partition_uri, AORC.hasRFC, rfc_office_uri))

    # Associate precip partition catalog with source dataset it holds
    g.add((precip_partition_uri, DCAT.dataset, source_dataset_node))


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
