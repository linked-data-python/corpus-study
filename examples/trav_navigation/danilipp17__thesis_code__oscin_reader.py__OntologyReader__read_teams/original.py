# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/reader.py
# region: OntologyReader._read_teams (lines 532-605, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, RDF, RDFS, XSD
from oscin.namespaces import (
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_SEQUENTIAL,
    HAS_DESCRIPTION,
    HAS_TITLE,
)

for term_uri in self.g.objects(
    team_uri, AGENTOSCIN.hasTerminationCondition
):
    if (term_uri, RDF.type, AGENTOSCIN.TurnLimitTermination) in self.g:
        mt = self._int_value(term_uri, AGENTOSCIN.hasMaxTurns)
        if mt is not None:
            max_turns = mt
            termination_conditions.append(
                {"type": "TurnLimit", "max_turns": mt}
            )
    elif (
        term_uri,
        RDF.type,
        AGENTOSCIN.EventBasedTermination,
    ) in self.g:
        trigger = self._str_value(
            term_uri, AGENTOSCIN.hasTriggerExpression
        ) or ""
        termination_conditions.append(
            {"type": "EventBased", "trigger": trigger}
        )
    elif (
        term_uri,
        RDF.type,
        AGENTOSCIN.RoutingTermination,
    ) in self.g:
        termination_conditions.append({"type": "Routing"})
    elif (
        term_uri,
        RDF.type,
        AGENTOSCIN.CompositeTermination,
    ) in self.g:
        operator = (
            self._str_value(term_uri, AGENTOSCIN.hasOperator) or "OR"
        )
        sub_conditions: list[dict] = []
        for sub_uri in self.g.objects(
            term_uri, AGENTOSCIN.hasSubCondition
        ):
            if (
                sub_uri,
                RDF.type,
                AGENTOSCIN.EventBasedTermination,
            ) in self.g:
                trigger = (
                    self._str_value(
                        sub_uri, AGENTOSCIN.hasTriggerExpression
                    )
                    or ""
                )
                sub_conditions.append(
                    {"type": "EventBased", "trigger": trigger}
                )
            elif (
                sub_uri,
                RDF.type,
                AGENTOSCIN.TurnLimitTermination,
            ) in self.g:
                mt = self._int_value(sub_uri, AGENTOSCIN.hasMaxTurns)
                if mt is not None:
                    sub_conditions.append(
                        {"type": "TurnLimit", "max_turns": mt}
                    )
                    # Promote to team-level so the generator can
                    # emit the MaxMessageTermination call.
                    if max_turns is None:
                        max_turns = mt
        termination_conditions.append(
            {
                "type": "Composite",
                "operator": operator,
                "conditions": sub_conditions,
            }
        )
