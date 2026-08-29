# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/extras/describer.py
# region: Describer.rev (lines 205-230, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib.py3compat import format_doctest_out

@format_doctest_out
def rev(self, p, s=None, **kws):
    """
    Same as ``rel``, but uses current subject as *object* of the relation.
    The given resource is still used as subject in the returned context
    manager.

    Usage::

        >>> from rdflib import URIRef
        >>> from rdflib.namespace import RDF, RDFS
        >>> d = Describer(about="http://example.org/")
        >>> with d.rev(RDFS.seeAlso, "http://example.net/"):
        ...     d.value(RDFS.label, "Net")
        >>> (URIRef('http://example.net/'), RDFS.seeAlso,
        ...         URIRef('http://example.org/')) in d.graph
        True
        >>> d.graph.value(URIRef('http://example.net/'), RDFS.label)
        rdflib.term.Literal(%(u)s'Net')

    """
    kws.setdefault('base', self.base)
    p = cast_identifier(p)
    s = cast_identifier(s, **kws)
    self.graph.add((s, p, self._current()))
    return self._subject_stack(s)
