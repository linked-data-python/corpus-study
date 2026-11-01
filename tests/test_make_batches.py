"""The batch plan skips settled drafts without changing the seeded order."""

import importlib.util
import random
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "make_batches.py"
_spec = importlib.util.spec_from_file_location("make_batches", SCRIPT)
make_batches = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_batches)

TODO = ["r%02d" % i for i in range(12)]


def test_a_settled_draft_is_not_proposed_again():
    picked = make_batches.pick(TODO, set(TODO[:6]), random.Random(1), 12)
    assert picked == TODO[6:]


def test_settled_drafts_are_dropped_after_the_shuffle():
    """Same generator state after the stratum, and the same order among the
    drafts that remain: what the campaigns followed is reproduced."""
    plain, skipping = random.Random(7), random.Random(7)
    make_batches.pick(TODO, set(), plain, 12)
    shuffled = list(TODO)
    random.Random(7).shuffle(shuffled)
    settled = set(shuffled[:2])
    picked = make_batches.pick(TODO, settled, skipping, 4)
    assert picked == sorted([n for n in shuffled if n not in settled][:4])
    assert plain.random() == skipping.random()
