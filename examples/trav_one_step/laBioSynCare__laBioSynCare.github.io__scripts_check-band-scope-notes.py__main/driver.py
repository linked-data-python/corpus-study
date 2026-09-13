"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_check-band-scope-notes.py__main.

`main` takes no argument: it discovers its own input files through
`module_paths()`/`instance_paths()` (see shim.py), which both versions get
from the same shim, pointed at `fixture_module.ttl` and
`fixture_instance.ttl`. So there is no `fixture=` graph to hand to `entry`;
the oracle is still the reading oracle (design record corpus/405) -- same
input graph on disk, same values (here: the printed report and the exit
code) out.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='main',
    calls=[((), {})],
)
