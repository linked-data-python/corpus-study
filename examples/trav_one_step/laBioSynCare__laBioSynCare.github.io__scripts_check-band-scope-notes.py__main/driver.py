"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_check-band-scope-notes.py__main.

`main` takes no argument: it discovers its own input files through
`module_paths()`/`instance_paths()` (see shim.py), which both versions get
from the same shim, pointed at `fixture_module.ttl` and
`fixture_instance.ttl`. So there is no `fixture=` graph to hand to `entry`;
the oracle is still the reading oracle (design record corpus/405) -- same
input graph on disk, same values (here: the printed report and the exit
code) out.

Repair 2026-10-30 (triage: weak-oracle).  The first driver compared only
the exit code, always 1: main() writes its failure report on STDERR, which
the harness does not capture, so every one of the region's reads could be
corrupted without the verdict moving.  The entry is now `demo`, a harness
function added identically to both sides (see the end of original.py): it
captures stderr and returns (exit code, stderr text), and it can point
module_paths()/instance_paths() at other files.  The harness compares the
pair and, separately, what each side prints on stdout (the success line).

Calls:

0. demo() -- the first driver's only call, main() on shim.py's files,
   now with its stderr report compared: an outcome word in a scopeNote, a
   neighbour that is not a band, four moved associations missing, an
   oscillation with no band or range.
1. everything passes (fixture_pass_*.ttl): return 0 and the success line,
   whose counts -- 7 bands, 10 labels and notes checked (two values of
   one predicate, an empty scopeNote among them), 6 oscillations, 7 band
   intervals -- observe sections 1 and 3; every association count is
   exactly at its threshold, so a read that lost a solution fails.  A
   decoy listed first carries every predicate read; skos:note and
   skos:editorialNote (outcome words, other predicates) and a blank-node
   band must not count; falsy values ("0" bounds, "" note) are present.
2. one failure per check (fixture_fail_*.ttl): an outcome word under each
   of the four skos predicates, hzMin > hzMax, a band with only hzMin,
   another with only hzMax, a range starting above / ending below its
   band, extendedHzMin == extendedHzMax, no extendedHzMax, a band without
   interval used as typical band, no typical band, two extendedHzMin of
   which the first decides, and association counts one below threshold
   next to neighbours a widened read would count.
3. no band at all (fixture_nobands_module.ttl): the vacuous-lint failure.
4. no file at all: an empty graph.
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent


def files(*names):
    return [HERE / n for n in names]


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        ((), {}),
        ((files("fixture_pass_module.ttl"), files("fixture_pass_instance.ttl")), {}),
        ((files("fixture_fail_module.ttl"), files("fixture_fail_instance.ttl")), {}),
        ((files("fixture_nobands_module.ttl"), files("fixture_pass_instance.ttl")), {}),
        (([], []), {}),
    ],
)
