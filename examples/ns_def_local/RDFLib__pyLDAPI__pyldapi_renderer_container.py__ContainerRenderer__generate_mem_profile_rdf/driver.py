"""Validation driver for RDFLib__pyLDAPI__pyldapi_renderer_container.py__ContainerRenderer__generate_mem_profile_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is an unbound method (`def _generate_mem_profile_rdf(self): ...`),
so the fixture is a stand-in `self` carrying every attribute the body reads:
`instance_uri`, `label`, `comment`, `members` (one entry of each of the three
shapes the code branches on), `request.query_params`, `per_page`, `page`,
`last_page`, `parent_container_uri` and `parent_container_label` (both
branches of the `is not None` checks are exercised: page 2 of 5, a parent
container with its own label).
"""
from types import SimpleNamespace

from rdfeval.harness import run_pair


def _fake_container():
    # types.SimpleNamespace (not a plain class) so the harness's own
    # arg[0]-after-the-call comparison (it checks the region did not mutate
    # what it was handed) has a working `==` to compare with: a plain class
    # instance would compare by identity and fail on two separate instances
    # even though neither side mutates it.
    return SimpleNamespace(
        instance_uri="http://example.org/container/1",
        label="Container One",
        comment="A container of members.",
        members=[
            {"uri": "http://example.org/member/1", "title": "Member One"},
            ("http://example.org/member/2", "Member Two"),
            "http://example.org/member/3",
        ],
        request=SimpleNamespace(query_params={"foo": "bar"}),
        per_page=20,
        page=2,
        last_page=5,
        parent_container_uri="http://example.org/container/0",
        parent_container_label="Parent Container",
    )


VERDICT = run_pair(
    __file__,
    entry='_generate_mem_profile_rdf',
    calls=[lambda: ((_fake_container(),), {})],
)
