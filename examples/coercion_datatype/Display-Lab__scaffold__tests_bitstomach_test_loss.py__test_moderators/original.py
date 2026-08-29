# Extracted from Display-Lab/scaffold@d368cfe17c : tests/bitstomach/test_loss.py
# region: test_moderators (lines 398-432, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, BNode, Graph, Literal
from src.bitstomach.signals import Loss
from src.utils.namespace import FHIR, PSDO, SLOWMO

def test_moderators():
    gap = -0.02
    prior_gap = 0.03
    slope = -0.1
    graph = Graph()
    r = graph.resource(BNode())
    # add loss types
    r.add(RDF.type, PSDO.performance_gap_content)
    r.add(RDF.type, PSDO.performance_trend_content)
    r.add(RDF.type, PSDO.loss_content)

    # add loss properites
    r.add(SLOWMO.PerformanceGapSize, Literal(gap))
    r.add(SLOWMO.PerformanceTrendSlope, Literal(slope))
    r.add(SLOWMO.PriorPerformanceGapSize, Literal(prior_gap))
    r.add(SLOWMO.StreakLength, Literal(3))
    r.add(SLOWMO.RegardingMeasure, BNode("PONV05"))

    # Add the comparator
    c = graph.resource(BNode())
    c.set(RDF.type, PSDO.peer_90th_percentile_benchmark)
    c.set(RDF.value, Literal(95.0))
    r.add(SLOWMO.RegardingComparator, c)

    moderators = Loss.moderators([r])

    moderator = [
        moderator
        for moderator in moderators
        if moderator["comparator_type"] == PSDO.peer_90th_percentile_benchmark
    ][0]

    assert moderator["comparison_size"] == abs(gap)
    assert moderator["trend_size"] == abs(slope) * 2
    assert moderator["prior_comparison_size"] == abs(prior_gap)
