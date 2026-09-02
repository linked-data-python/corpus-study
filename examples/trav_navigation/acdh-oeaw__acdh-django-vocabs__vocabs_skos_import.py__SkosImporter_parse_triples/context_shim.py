# Context shim (see meta.json): rdflib.Graph.preferredLabel, verbatim from
# rdflib 5.0.0's rdflib/graph.py (lines 722-795) -- the exact release range
# this project's OWN requirements.txt/setup.py pin (`rdflib>=5.0.0,<7`, both
# checked directly against the corpus clone). The method was removed from
# the rdflib series this study pins (7.2.1, for cross-region reproducibility
# -- see the corpus-study README) sometime before 7.0: `hasattr(Graph,
# "preferredLabel")` is False under the venv's rdflib, confirmed directly.
#
# This restores a missing BINDING, the same kind of gap AGENT_BATCH.md's
# "163 regions" note is about, except the gap is in rdflib itself rather
# than in the region's own project -- not a rewrite of the region's call
# site, which stays `g.preferredLabel(cs, labelProperties=(...))`,
# unchanged, on both sides. Not the system under test: preferredLabel is
# incidental API this region happens to use for its "title" field, entirely
# unrelated to the multi-pattern-read constructions (m{ }, .first(),
# bool(m{ })) this batch is about, and its own algorithm is untouched by
# the translation either way.
from rdflib import Graph


def _preferredLabel(self, subject, lang=None, default=None,
                     labelProperties=None):
    from rdflib.namespace import RDFS, SKOS
    if labelProperties is None:
        labelProperties = (SKOS.prefLabel, RDFS.label)
    if default is None:
        default = []

    if lang is not None:
        if lang == "":

            def langfilter(l):
                return l.language is None

        else:

            def langfilter(l):
                return l.language == lang

    else:

        def langfilter(l):
            return True

    for labelProp in labelProperties:
        labels = list(filter(langfilter, self.objects(subject, labelProp)))
        if len(labels) == 0:
            continue
        else:
            return [(labelProp, l) for l in labels]
    return default


Graph.preferredLabel = _preferredLabel
