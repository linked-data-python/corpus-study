# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/engine/trace_obsels.py
# region: AbstractTraceObsels._detect_mon_change (lines 483-541, stratum trav_one_step)
# licence of the source repository: see meta.json
from itertools import chain
from ..namespace import KTBS

def _detect_mon_change(self, graph, prepared):
    """Detect monotonicity changed induced by 'graph', and update `prepared` accordingly.

    Note that this is called after graph has been added to self.state,
    so all arcs from graph are also in state.
    """
    trace_uri = self.trace_uri
    new_obs = graph.value(None, KTBS.hasTrace, trace_uri)
    if prepared.last_obsel is None:
        prepared.last_obsel = new_obs
        prepared.last_begin = int(graph.value(new_obs, KTBS.hasBegin))
        prepared.last_end = int(graph.value(new_obs, KTBS.hasEnd))
        return

    old_last_obsel = prepared.last_obsel
    old_last_begin = prepared.last_begin
    old_last_end = prepared.last_end
    pseudomon_range = self.trace.pseudomon_range
    pse_mon_b_limit = old_last_begin - pseudomon_range
    pse_mon_e_limit = old_last_end - pseudomon_range

    str_mon = True
    pse_mon = True
    self_state_value = self.state.value
    # we used a SPARQL query before, but this seems to be more efficient...
    # check all new obsels, but also their *related* obsels
    # (as the relation changes *both* obsels)
    for obs in chain( [new_obs],
                      graph.objects(new_obs, None),
                      graph.subjects(None, new_obs)):
        if not obs.startswith(trace_uri):
            continue # not an obsel of this trace, skip it
        end = self_state_value(obs, KTBS.hasEnd)
        if end is None:
            continue # not an obsel, skip it
        end = int(end)
        begin = None
        if end < old_last_end:
            str_mon = False
            if end < pse_mon_e_limit:
                pse_mon = False
        elif end == old_last_end:
            begin = int(self_state_value(obs, KTBS.hasBegin))
            if begin < old_last_begin:
                str_mon = False
                if begin < pse_mon_b_limit:
                    pse_mon = False
            elif begin == old_last_begin:
                if obs <= old_last_obsel:
                    str_mon = False
        if obs is new_obs and str_mon:
            prepared.last_obsel = new_obs
            if begin is None:
                begin = int(graph.value(new_obs, KTBS.hasBegin))
            prepared.last_begin = begin
            prepared.last_end = end

    prepared.str_mon = prepared.str_mon and str_mon
    prepared.pse_mon = prepared.pse_mon and pse_mon
