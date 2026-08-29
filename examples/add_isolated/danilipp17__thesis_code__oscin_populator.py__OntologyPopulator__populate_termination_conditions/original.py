# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/populator.py
# region: OntologyPopulator._populate_termination_conditions (lines 711-776, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from oscin.namespaces import (
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_HIERARCHICAL,
    COORD_NETWORK,
    COORD_REACT_LOOP,
    COORD_ROUND_ROBIN,
    COORD_SELECTOR_BASED,
    COORD_SEQUENTIAL,
    COORD_SWARM,
    HAS_DESCRIPTION,
    HAS_REFERENCE,
    HAS_TITLE,
    make_instance_namespace,
)

def _populate_termination_conditions(
    self, team_uri: URIRef, team_key: str, conditions: list[dict]
) -> None:
    """Populate structured termination conditions from parser data."""
    for i, tc in enumerate(conditions):
        tc_type = tc.get("type", "")
        suffix = f"{team_key}_{i}"

        if tc_type == "EventBased":
            tc_uri = self._create_individual(
                "EventTermination", suffix, AGENTOSCIN.EventBasedTermination
            )
            trigger = tc.get("trigger", "")
            if trigger:
                self._add_str(tc_uri, AGENTOSCIN.hasTriggerExpression, trigger)
            self.g.add((team_uri, AGENTOSCIN.hasTerminationCondition, tc_uri))

        elif tc_type == "TurnLimit":
            tc_uri = self._create_individual(
                "TurnLimit", suffix, AGENTOSCIN.TurnLimitTermination
            )
            max_turns = tc.get("max_turns")
            if max_turns is not None:
                self._add_int(tc_uri, AGENTOSCIN.hasMaxTurns, int(max_turns))
            self.g.add((team_uri, AGENTOSCIN.hasTerminationCondition, tc_uri))

        elif tc_type == "Routing":
            tc_uri = self._create_individual(
                "RoutingTermination", suffix, AGENTOSCIN.RoutingTermination
            )
            self.g.add((team_uri, AGENTOSCIN.hasTerminationCondition, tc_uri))

        elif tc_type == "Composite":
            comp_uri = self._create_individual(
                "CompositeTermination", suffix, AGENTOSCIN.CompositeTermination
            )
            operator = tc.get("operator", "OR")
            self._add_str(comp_uri, AGENTOSCIN.hasOperator, operator)
            # Recurse for sub-conditions
            sub_conditions = tc.get("conditions", [])
            for j, sub_tc in enumerate(sub_conditions):
                sub_suffix = f"{suffix}_sub{j}"
                sub_type = sub_tc.get("type", "")
                if sub_type == "EventBased":
                    sub_uri = self._create_individual(
                        "EventTermination",
                        sub_suffix,
                        AGENTOSCIN.EventBasedTermination,
                    )
                    trigger = sub_tc.get("trigger", "")
                    if trigger:
                        self._add_str(
                            sub_uri, AGENTOSCIN.hasTriggerExpression, trigger
                        )
                    self.g.add((comp_uri, AGENTOSCIN.hasSubCondition, sub_uri))
                elif sub_type == "TurnLimit":
                    sub_uri = self._create_individual(
                        "TurnLimit", sub_suffix, AGENTOSCIN.TurnLimitTermination
                    )
                    max_turns = sub_tc.get("max_turns")
                    if max_turns is not None:
                        self._add_int(
                            sub_uri, AGENTOSCIN.hasMaxTurns, int(max_turns)
                        )
                    self.g.add((comp_uri, AGENTOSCIN.hasSubCondition, sub_uri))
            self.g.add((team_uri, AGENTOSCIN.hasTerminationCondition, comp_uri))
