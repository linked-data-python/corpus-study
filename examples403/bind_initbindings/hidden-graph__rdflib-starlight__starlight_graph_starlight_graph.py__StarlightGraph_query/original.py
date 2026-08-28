# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/graph/starlight_graph.py
# region: StarlightGraph.query (lines 1368-1370, stratum bind_initbindings)
# licence of the source repository: see meta.json
r = raw.query(query_object, processor=processor, result=result,
              initNs=initNs, initBindings=init_bindings,
              use_store_provided=use_store_provided, **kwargs)
