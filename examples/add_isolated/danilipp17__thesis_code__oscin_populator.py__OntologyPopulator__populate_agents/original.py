# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/populator.py
# region: OntologyPopulator._populate_agents (lines 204-276, stratum add_isolated)
# licence of the source repository: see meta.json
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

if directive == "ModelDirective":
    prompt_uri = self._create_individual(
        "AgentPrompt", key, AGENTO.Prompt
    )
    self.prompt_uris[f"agent_{key}"] = prompt_uri
    self._add_str(prompt_uri, AGENTO.promptInstruction, agent.goal)
    self._add_str(prompt_uri, AGENTO.promptContext, agent.backstory)
    self._add_str(
        prompt_uri, AGENTOSCIN.hasDirectiveFunction, "ModelDirective"
    )
    if agent.prompt_source:
        self._add_str(
            prompt_uri, AGENTOSCIN.hasSourceAttribute, agent.prompt_source
        )
    self.g.add((uri, AGENTO.agentPrompt, prompt_uri))

    if agent.description:
        orch_prompt_uri = self._create_individual(
            "OrchestratorPrompt", key, AGENTO.Prompt
        )
        self._add_str(
            orch_prompt_uri,
            AGENTO.promptInstruction,
            agent.description,
        )
        self._add_str(
            orch_prompt_uri,
            AGENTOSCIN.hasDirectiveFunction,
            "OrchestratorDirective",
        )
        self._add_str(
            orch_prompt_uri,
            AGENTOSCIN.hasSourceAttribute,
            "description",
        )
        self.g.add((uri, AGENTO.agentPrompt, orch_prompt_uri))
elif directive == "DualDirective":
    prompt_uri = self._create_individual(
        "AgentPrompt", key, AGENTO.Prompt
    )
    self.prompt_uris[f"agent_{key}"] = prompt_uri

    instruction = (
        f"{agent.role}: {agent.goal}" if agent.goal else agent.role
    )
    self._add_str(prompt_uri, AGENTO.promptInstruction, instruction)
    self._add_str(prompt_uri, AGENTO.promptContext, agent.backstory)
    self._add_str(
        prompt_uri, AGENTOSCIN.hasDirectiveFunction, "DualDirective"
    )
    if agent.prompt_source:
        self._add_str(
            prompt_uri, AGENTOSCIN.hasSourceAttribute, agent.prompt_source
        )
    self.g.add((uri, AGENTO.agentPrompt, prompt_uri))
elif agent.goal or agent.backstory:
    prompt_uri = self._create_individual(
        "AgentPrompt", key, AGENTO.Prompt
    )
    self.prompt_uris[f"agent_{key}"] = prompt_uri
    if agent.goal:
        self._add_str(prompt_uri, AGENTO.promptInstruction, agent.goal)
    if agent.backstory:
        self._add_str(prompt_uri, AGENTO.promptContext, agent.backstory)
    if directive:
        self._add_str(
            prompt_uri, AGENTOSCIN.hasDirectiveFunction, directive
        )
    if agent.prompt_source:
        self._add_str(
            prompt_uri, AGENTOSCIN.hasSourceAttribute, agent.prompt_source
        )
    self.g.add((uri, AGENTO.agentPrompt, prompt_uri))
