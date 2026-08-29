# Extracted from weso/rdfsync@fd58206d89 : rdfsync/wb2rdf/conversion.py
# region: Converter.execute_synchronization (lines 522-526, stratum remove)
# licence of the source repository: see meta.json
if bnodes_of_rdf:
    for key in bnodes_of_rdf.keys():
        for value in bnodes_of_rdf[key]:
            self.graph.remove((value, None, None))
            self.graph.remove((None, None, value))
