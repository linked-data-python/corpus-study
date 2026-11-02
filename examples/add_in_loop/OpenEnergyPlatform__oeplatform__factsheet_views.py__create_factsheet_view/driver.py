"""Validation driver for OpenEnergyPlatform__oeplatform__factsheet_views.py__create_factsheet_view.

The region is the loop of the view that writes the publications of a
factsheet into the graph `bundle`.  entry=None: both modules are executed and
the graph `bundle` they leave behind is compared by isomorphism (plus the
module values: the loop variables, the last publication and author).

context_shim.py supplies the loop's free variables; its four publications
span the branches: all optional fields present (with control characters in
the title, removed by `remove_non_printable`, two authors), all of them empty
(no label, no doi, no date, no report), the placeholder date "01-01-1900"
(skipped) with an author already added by an earlier publication, and a doi
that is None (the original writes the literal "None") with a date that is
not a full xsd:dateTime lexical form.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
