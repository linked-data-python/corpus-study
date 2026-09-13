# Context shim (see meta.json): stand-ins for the Django project pieces
# used by apps/visualisation/views.py in
# aminedouiri/knowledge-formalization-web-application, so the region
# executes outside the Django project (no settings module, no database).
# `render` returns the context dict it would otherwise pass to the Django
# template engine, and `Connaissance`/`Commentaire` mimic just the two
# queryset calls the region makes (`.objects.filter(status_vue=False).count()`
# and `.objects.all().count()`) against a fixed in-memory row set. Identical
# bindings for both representations.


class _QuerySet:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, **kwargs):
        return _QuerySet([r for r in self._rows
                           if all(r.get(k) == v for k, v in kwargs.items())])

    def all(self):
        return self

    def count(self):
        return len(self._rows)


class Connaissance:
    objects = _QuerySet([
        {"status_vue": False},
        {"status_vue": False},
        {"status_vue": True},
    ])


class Commentaire:
    objects = _QuerySet([{}, {}])


def render(request, template_name, context=None):
    return context
