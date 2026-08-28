# Extracted from Dewberry/blobfish@db89f34228 : blobfish/aorc/parse_composite.py
# region: create_graph_triples (lines 119-167, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import DCAT, DCTERMS, OWL, PROV, RDF, XSD, Graph, URIRef, BNode, Literal
from ..pyrdf import AORC

def create_graph_triples(meta: CompletedCompositeMetadata, merged_graph: Graph, node_namer: NodeNamer):
    # Create composite dataset
    composite_dataset_uri = URIRef(meta.composite_s3_directory)
    merged_graph.add((composite_dataset_uri, RDF.type, AORC.CompositeDataset))

    # Add composite dataset properties
    composite_dataset_period_of_time_node = BNode(node_namer.name_ds_period(meta))
    merged_graph.add((composite_dataset_period_of_time_node, RDF.type, DCTERMS.PeriodOfTime))
    merged_graph.add((composite_dataset_uri, DCTERMS.temporal, composite_dataset_period_of_time_node))
    start_time = Literal(meta.start_time, datatype=XSD.dateTime)
    end_time = Literal(meta.end_time, datatype=XSD.dateTime)
    merged_graph.add((composite_dataset_period_of_time_node, DCAT.startDate, start_time))
    merged_graph.add((composite_dataset_period_of_time_node, DCAT.endDate, end_time))

    # Create distribution
    composite_distribution_uri = URIRef(meta.public_uri)
    merged_graph.add((composite_distribution_uri, RDF.type, AORC.CompositeDistribution))
    netcdf_format = URIRef("https://publications.europa.eu/resource/authority/file-type/NETCDF")
    merged_graph.add((composite_distribution_uri, DCAT.packageFormat, netcdf_format))
    last_modified = Literal(meta.composite_last_modified, datatype=XSD.dateTime)
    merged_graph.add((composite_dataset_uri, DCTERMS.created, last_modified))
    access_description = Literal(
        "Access is restricted based on users credentials for AWS bucket holding data", datatype=XSD.string
    )
    merged_graph.add((composite_distribution_uri, OWL.Annotation, access_description))

    # Create docker image
    docker_image_uri = URIRef(meta.docker_image_url)
    merged_graph.add((docker_image_uri, RDF.type, AORC.DockerImage))

    # Create composite job
    composite_job_node = BNode(node_namer.name_composite_job(meta))
    merged_graph.add((composite_job_node, RDF.type, AORC.CompositeJob))

    # Create script
    composite_script_node = BNode(meta.composite_script)
    merged_graph.add((composite_script_node, RDF.type, AORC.CompositeScript))
    merged_graph.add((composite_script_node, DCTERMS.identifier, Literal(meta.composite_script)))

    # Associate docker image, script, job, and dataset generated
    merged_graph.add((composite_dataset_uri, AORC.wasCompositedBy, composite_job_node))
    merged_graph.add((composite_job_node, PROV.wasStartedBy, composite_script_node))
    merged_graph.add((composite_script_node, AORC.hasDockerImage, docker_image_uri))

    # Associate members of composite with composite dataset and composite job
    for member_dataset in meta.get_member_datasets():
        member_dataset_uri = URIRef(member_dataset)
        merged_graph.add((composite_dataset_uri, AORC.isCompositeOf, member_dataset_uri))
        merged_graph.add((composite_job_node, PROV.used, member_dataset_uri))
