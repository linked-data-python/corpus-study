# Extracted from tetherless-world/setlr@09baa95fb2 : setlr/core.py
# region: transform (lines 798-844, stratum remove)
# licence of the source repository: see meta.json
import rdflib
csvw = rdflib.Namespace('http://www.w3.org/ns/csvw#')
setl = rdflib.Namespace('http://purl.org/twc/vocab/setl/')
prov = rdflib.Namespace('http://www.w3.org/ns/prov#')
sp = rdflib.Namespace('http://spinrdf.org/sp#')
logger = None

def transform(transform_resource, resources):
    logger.info('Transforming %s',transform_resource.identifier)

    transform_graph = rdflib.ConjunctiveGraph()
    for result in transform_graph.subjects(prov.wasGeneratedBy):
        transform_graph = rdflib.ConjunctiveGraph(identifier=result.identifier)

    used = set(transform_resource[prov.used])

    for csv_file in [u for u in used if u[rdflib.RDF.type:csvw.Table]]:
        csv_graph = rdflib.Graph(store=transform_graph.store,
                                 identifier=csv_file)
        csv_graph += resources[csv_file.identifier]


    for script in [u for u in used if u[rdflib.RDF.type:setl.PythonScript]]:
        logger.info("Script: %s", script.identifier)
        s = script.value(prov.value).value
        local_vars = dict(graph = transform_graph, setl_graph = transform_resource.graph)
        global_vars = dict()
        exec(s, global_vars, local_vars)

    for jsldt in [u for u in used if u[rdflib.RDF.type:setl.PythonScript]]:
        logger.info("Script: %s", script.identifier)
        s = script.value(prov.value).value
        local_vars = dict(graph = transform_graph, setl_graph = transform_resource.graph)
        global_vars = dict()
        exec(s, global_vars, local_vars)

    for update in [u for u in used if u[rdflib.RDF.type:sp.Update]]:
        logger.info("Update: %s", update.identifier)
        query = update.value(prov.value).value
        transform_graph.update(query)

    for construct in [u for u in used if u[rdflib.RDF.type:sp.Construct]]:
        logger.info("Construct: %s", construct.identifier)
        query = construct.value(prov.value).value
        g = transform_graph.query(query)
        transform_graph += g

    for csv_file in [u for u in used if u[rdflib.RDF.type:csvw.Table]]:
        g = rdflib.Graph(identifier=csv_file.identifier,store=transform_graph.store)
        g.remove((None, None, None))
        transform_graph.store.remove_graph(csv_file.identifier)

    for result in transform_graph.subjects(prov.wasGeneratedBy):
        resources[result.identifier] = transform_graph
