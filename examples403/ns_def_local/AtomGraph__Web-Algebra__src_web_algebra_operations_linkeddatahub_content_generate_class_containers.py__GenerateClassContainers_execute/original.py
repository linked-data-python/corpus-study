# Extracted from AtomGraph/Web-Algebra@128e184aa8 : src/web_algebra/operations/linkeddatahub/content/generate_class_containers.py
# region: GenerateClassContainers.execute (lines 57-163, stratum ns_def_local)
# licence of the source repository: see meta.json
import logging
from rdflib import URIRef, Literal, Namespace, Graph
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS
from rdflib.query import Result
from web_algebra.operations.linkeddatahub.create_item import CreateItem
from web_algebra.operations.linked_data.post import POST
from web_algebra.operations.linkeddatahub.content.add_object_block import AddObjectBlock
from web_algebra.json_result import JSONResult

def execute(self, ontology: Graph, parent_container: URIRef, endpoint: URIRef, service_uri: URIRef) -> Result:
    """Create LDH items for ontology classes

    Args:
        ontology: RDF graph containing classes
        parent_container: URI of parent container where class items will be created
        endpoint: SPARQL endpoint URI used for query text generation
        service_uri: URI of the global SPARQL service resource

    Returns:
        Concatenated Result containing all operation results (CreateItem + POST + AddObjectBlock bindings)
    """
    if not isinstance(ontology, Graph):
        raise TypeError(
            f"GenerateClassContainers operation expects 'ontology' to be Graph, got {type(ontology)}"
        )
    if not isinstance(parent_container, URIRef):
        raise TypeError(
            f"GenerateClassContainers operation expects 'parent_container' to be URIRef, got {type(parent_container)}"
        )
    if not isinstance(endpoint, URIRef):
        raise TypeError(
            f"GenerateClassContainers operation expects 'endpoint' to be URIRef, got {type(endpoint)}"
        )
    # Define namespaces
    LDH = Namespace("https://w3id.org/atomgraph/linkeddatahub#")
    SP = Namespace("http://spinrdf.org/sp#")
    SPIN = Namespace("http://spinrdf.org/spin#")
    AC = Namespace("https://w3id.org/atomgraph/client#")

    # Query to find all classes in the ontology
    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT ?class
    WHERE {
      ?class a owl:Class .
      FILTER (!isBlank(?class))
    }
    ORDER BY ?class
    """

    results = ontology.query(query)

    # Collect all operation results and track unique variables
    all_bindings = []
    all_vars = set()

    # Create container for each class
    for row in results:
        row_dict = row.asdict()
        class_uri = row_dict["class"]

        # Validate
        if not isinstance(class_uri, URIRef):
            raise TypeError(f"Expected class to be URIRef, got {type(class_uri)}")

        # Extract local name for URI
        class_local = self._get_local_name(class_uri)

        logging.info(f"Creating item for class {class_uri}")

        # Step 1: Create item
        title = Literal(f"{class_local} instances", datatype=XSD.string)
        slug = Literal(class_local, datatype=XSD.string)

        create_result = CreateItem(settings=self.settings, context=self.context).execute(
            parent_container, title, slug
        )

        all_bindings.extend(create_result.bindings)
        all_vars.update(create_result.vars)

        item_uri = URIRef(create_result.bindings[0]["url"])
        logging.info(f"Created item at {item_uri}")

        # Step 2: POST sp:Select query
        query_uri = URIRef(f"{item_uri}#Instances_Query")
        sparql_text = self._generate_instance_query(class_uri)

        query_graph = self._build_query_graph(query_uri, class_local, sparql_text, service_uri, LDH, SP)
        post_query_result = POST(settings=self.settings, context=self.context).execute(item_uri, query_graph)
        all_bindings.extend(post_query_result.bindings)
        all_vars.update(post_query_result.vars)
        logging.info(f"Posted query to {item_uri}")

        # Step 3: POST ldh:View
        view_uri = URIRef(f"{item_uri}#Instances_View")
        view_graph = self._build_view_graph(view_uri, class_local, query_uri, service_uri, LDH, SP, AC, SPIN)
        post_view_result = POST(settings=self.settings, context=self.context).execute(item_uri, view_graph)
        all_bindings.extend(post_view_result.bindings)
        all_vars.update(post_view_result.vars)
        logging.info(f"Posted view to {item_uri}")

        # Step 4: Add object block to surface the view in the item
        add_block_result = AddObjectBlock(settings=self.settings, context=self.context).execute(
            url=item_uri,
            value=view_uri,
            title=Literal(f"All {class_local}", datatype=XSD.string),
            fragment=Literal("InstancesBlock", datatype=XSD.string)
        )
        all_bindings.extend(add_block_result.bindings)
        all_vars.update(add_block_result.vars)
        logging.info(f"Added object block to {item_uri}")

    # Create concatenated Result using JSONResult
    return JSONResult(list(all_vars), all_bindings)
