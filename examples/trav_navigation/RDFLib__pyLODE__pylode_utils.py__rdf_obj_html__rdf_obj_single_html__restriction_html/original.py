# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/utils.py
# region: rdf_obj_html._rdf_obj_single_html._restriction_html (lines 776-870, stratum trav_navigation)
# licence of the source repository: see meta.json
from dominate.util import raw
from rdflib.paths import ZeroOrMore

def _restriction_html(ont__, obj__, ns__):
    prop = None
    card = None
    cls = None

    for px, o in ont__.predicate_objects(obj__):
        if px != RDF.type:
            if px == OWL.onProperty:
                prop = _hyperlink_html(ont__, o, back_onts_, ns__, fids_)
            # Added the onClass restriction otherwise the class name is ignored in the HTML output.
            elif px == OWL.onClass:
                if (o, OWL.unionOf | OWL.intersectionOf, None) in ont__:
                    cls = _setclass_html(ont__, o, back_onts_, ns__, fids_)
                else:
                    cls = _hyperlink_html(
                        ont__, o, back_onts_, ns__, fids_, OWL.Class
                    )
            elif px in RESTRICTION_TYPES + OWL_SET_TYPES:
                if px in [
                    OWL.minCardinality,
                    OWL.minQualifiedCardinality,
                    OWL.maxCardinality,
                    OWL.maxQualifiedCardinality,
                    OWL.cardinality,
                    OWL.qualifiedCardinality,
                ]:
                    if px in [OWL.minCardinality, OWL.minQualifiedCardinality]:
                        card = "min"
                    elif px in [
                        OWL.maxCardinality,
                        OWL.maxQualifiedCardinality,
                    ]:
                        card = "max"
                    elif px in [OWL.cardinality, OWL.qualifiedCardinality]:
                        card = "exactly"

                    card = span(span(card, _class="cardinality"), span(str(o)))
                else:
                    if px == OWL.allValuesFrom:
                        card = "only"
                    elif px == OWL.someValuesFrom:
                        card = "some"
                    elif px == OWL.hasValue:
                        card = "value"
                    elif px == OWL.unionOf:
                        card = "union"
                    elif px == OWL.intersectionOf:
                        card = "intersection"

                        card = span(
                            span(card, _class="cardinality"),
                            raw(_rdf_obj_single_html),
                        )

                    card = span(
                        span(card, _class="cardinality"),
                        span(
                            _hyperlink_html(
                                ont__, o, back_onts_, ns__, fids_, OWL.Class
                            )
                        ),
                    )
            elif px == ONTPUB.inRangeOf:  # rdfs:range
                for o2 in ont__.objects(o, RDFS.range):
                    for rp, ro in ont__.predicate_objects(o2):
                        if rp == OWL.onDatatype:
                            prop = _hyperlink_html(
                                ont__, ro, back_onts_, ns__, fids_
                            )
                        if rp == OWL.withRestrictions:
                            cards = []
                            for ro2 in ont__.objects(o2, OWL.withRestrictions):
                                for ro3 in ont__.objects(
                                    ro2, RDF.rest * ZeroOrMore / RDF.first
                                ):
                                    for rp4, ro4 in ont__.predicate_objects(
                                        ro3
                                    ):
                                        if rp4 in DATATYPE_CARDINALITIES.keys():
                                            cards.append(
                                                f"{DATATYPE_CARDINALITIES[rp4]}{ro4}"
                                            )
                            if len(cards) > 0:
                                card = " [" + ", ".join(cards) + "]"
                                # XXX

    # Combined the check for card and cls so that only one br is added.
    if card is not None and cls is not None:
        restriction = span(prop, card, cls, br())
    elif card is not None:
        restriction = span(prop, card, br())
    else:
        restriction = prop

    return span(restriction) if restriction is not None else "None"
