# Extracted from RMLio/RML2SHACL@72f8ae0cfd : src/RML.py
# region: RML.removeBlankNodesMultipleMaps (lines 171-239, stratum remove)
# licence of the source repository: see meta.json
import rdflib

def removeBlankNodesMultipleMaps(self):
    # loop over all the Triple Maps in the RML input file
    for sTM, pTM, oTM in self.graph.triples((None, None, self.r2rmlNS.TriplesMap)):
        graphHelp = {}
        graphsPOM = []
        graphTripleMap = rdflib.Graph()
        graphsubjectMap = rdflib.Graph()
        graphlogicalSource = rdflib.Graph()
        graphTripleMap.add((sTM, pTM, oTM))  # add triplesmap header
        graphHelp["TM"] = graphTripleMap
        tel = 0
        # inside one Triple Map we doe loops over:
        for s, p, o in self.graph.triples((sTM, None, None)):
            # the triples belonging to the Logical Source
            if p == self.rmlNS.logicalSource:
                for s2, p2, o2 in self.graph.triples((o, None, None)):
                    # searching for same Blank Node
                    # add logical source info
                    graphlogicalSource.add((p, p2, o2))
                graphHelp["LS"] = graphlogicalSource
            # the triples belonging to the Subject Map
            if p == self.SUBJECT_MAP:
                for s2, p2, o2 in self.graph.triples((o, None, None)):
                    # searching for same Blank Node
                    graphsubjectMap.add((p, p2, o2))
                # add subject Map  info
                graphHelp["SM"] = graphsubjectMap
            # the multiple triples that are PredicateObject Maps
            if p == self.POM:
                graphPredicatObjectMap = rdflib.Graph()
                # searching for one PredicatObjectMap
                # searching for same Blank Node
                for s2, p2, o2 in self.graph.triples((o, None, None)):
                    if p2 == self.r2rmlNS.predicateMap:
                        for s3, p3, o3 in self.graph.triples((o2, self.CONSTANT, None)):
                            # we make the "rr:predicateMap rr:constant o" triple to sthe shurtcut "rr:PredicateObjectMap rr:predicate o2"
                            graphPredicatObjectMap.add((p, self.PREDICATE, o3))
                    # add the predicateobjectMap with the constant transformed into rr:predicate instead of constant
                    else:
                        graphPredicatObjectMap.add((p, p2, o2))
                    # add the predicateobjectMap
                # searching for which objectMap belongs to this PredicateObjectMap
                for s2, p2, o2 in graphPredicatObjectMap.triples((p, self.OJBECT_MAP, None)):
                    for s3, p3, o3 in self.graph.triples((o2, None, None)):
                        graphPredicatObjectMap.add((p2, p3, o3))
                    # add the objectMap beloning to the predicateobjectMap added in previous loop
                    graphPredicatObjectMap.remove((s2, p2, o2))
                # remove something with a blanknode in that we added too much
                # if we don't have an rr:ObjectMap but an rr:object (as part of rr:predicateMap as an predicate)
                # we will write this as rr:ObjectMap rr:constant (object that belonged to the rr:object)
                for s2, p2, o2 in graphPredicatObjectMap.triples((p, self.OBJECT, None)):
                    # graphPredicatObjectMap.add((s2,p2,o2))
                    # #add the object beloning to the predicateobjectMap added in previous loop
                    graphPredicatObjectMap.add((self.OJBECT_MAP, self.CONSTANT, o2))
                    graphPredicatObjectMap.remove((s2, p2, o2))
                # remove the "rr:predicateMap rr:object o2" triple from the graph because it gets added in loop for objectMap
                # loop to find any possible RefObjectMaps
                for sROM, pROM, oROM in self.graph.triples((None, None, self.r2rmlNS.RefObjectMap)):
                    # if we find one we see if it belongs to the ObjectMap we are working with now
                    for s3, p3, o3 in self.graph.triples((p, self.OJBECT_MAP, sROM)):
                        # if this is the fact we search inside the RefObjectMap (sROM) for the value of rr:parentTriplesMap
                        for s4, p4, o4 in self.graph.triples((sROM, self.r2rmlNS.parentTriplesMap, None)):
                            graphPredicatObjectMap.add(
                                (self.OJBECT_MAP, self.r2rmlNS.parentTriplesMap, o4))
                # add the parentTriplesMap to the ObjectMap

                graphHelp["POM" + str(tel)] = graphPredicatObjectMap
                tel = tel + 1
        self.graphs.append(graphHelp)
