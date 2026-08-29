# Extracted from tgbugs/pyontutils@cb3efcd10f : pyontutils/combinators.py
# region: EquivalentClass.parse (lines 780-820, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from pyontutils.closed_namespaces import rdf, rdfs, owl

def parse(self, *triples, graph=None):
    if graph is None:  # TODO decorator for this
        graph = rdflib.Graph()
        [graph.add(t) for t in triples]

    for subject, ec_s in graph.subject_objects(self.predicate):
        #rdftype = next(graph.objects(subject, rdf.type))  # FIXME > 1
        def parts(predicate, object):
            #print('aaaaaaaaaaaaa', predicate, object)
            if predicate == rdf.type:
                if object != owl.Class:
                    raise TypeError('owl:equivalentClass members need to be owl:Classes not {rdftype}')
            elif predicate == self.operator:
                #yield subject, tuple((p, o) for p, o in graph.predicate_objects(object))
                for p, o in graph.predicate_objects(object):
                    typep = self.lift_rules[p]
                    if typep is None:
                        continue
                    print(p, typep)
                    if p == rdf.first:
                        # FIXME should not have to be explicit? or are lists special?
                        # equivalent class does not need explicit list combinatoring at the moment
                        # so we just get the objects in the list for now
                        # it looks weird on repr, but that is ok
                        yield from next(typep.parse(root=object, graph=graph)).objects
                    else:
                        #print('AAAAAAAAAAAAA', typep)
                        triples = ((o, _p, _o) for _p, _o in graph.predicate_objects(o))
                        yield from typep.parse(*triples)
                        #yield from typep.parse((o, _p, _o) for _p, _o in graph.predicate_objects(o))
            else:
                print(f'failed to parse {subject} owl:equivalentClass {predicate} != {self.operator}')

        # FIXME None to get them all?
        combinators = tuple(t for p, o in graph.predicate_objects(ec_s)
                       #for mt in parts(p, o)  # FIXME somewhere someone is not yielding properly
                       # no actually this is correct, it is just that there is indeed a list in there
                       # that is not property combinatored
                       #for t in mt)
                       for t in parts(p, o))
        yield subject, self(*combinators)
