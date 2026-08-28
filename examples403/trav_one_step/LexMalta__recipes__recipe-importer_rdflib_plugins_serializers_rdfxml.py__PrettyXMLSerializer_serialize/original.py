# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/plugins/serializers/rdfxml.py
# region: PrettyXMLSerializer.serialize (lines 167-238, stratum trav_one_step)
# licence of the source repository: see meta.json
from typing import IO, Dict, Optional, Set
from rdflib.namespace import RDF, RDFS, Namespace  # , split_uri
from rdflib.plugins.parsers.RDFVOC import RDFVOC
from rdflib.plugins.serializers.xmlwriter import XMLWriter
from rdflib.term import BNode, IdentifiedNode, Identifier, Literal, Node, URIRef
XMLBASE = "http://www.w3.org/XML/1998/namespacebase"

def serialize(
    self,
    stream: IO[bytes],
    base: Optional[str] = None,
    encoding: Optional[str] = None,
    **args,
):
    self.__serialized: Dict[Identifier, int] = {}
    store = self.store
    # if base is given here, use that, if not and a base is set for the graph use that
    if base is not None:
        self.base = base
    elif store.base is not None:
        self.base = store.base
    self.max_depth = args.get("max_depth", 3)
    assert self.max_depth > 0, "max_depth must be greater than 0"

    self.nm = nm = store.namespace_manager
    self.writer = writer = XMLWriter(stream, nm, encoding)
    namespaces = {}

    possible: Set[Node] = set(store.predicates()).union(
        store.objects(None, RDF.type)
    )

    for predicate in possible:
        # type error: Argument 1 to "compute_qname_strict" of "NamespaceManager" has incompatible type "Node"; expected "str"
        prefix, namespace, local = nm.compute_qname_strict(predicate)  # type: ignore[arg-type]
        namespaces[prefix] = namespace

    namespaces["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    writer.push(RDFVOC.RDF)

    if "xml_base" in args:
        writer.attribute(XMLBASE, args["xml_base"])
    elif self.base:
        writer.attribute(XMLBASE, self.base)

    writer.namespaces(namespaces.items())

    subject: IdentifiedNode
    # Write out subjects that can not be inline
    # type error: Incompatible types in assignment (expression has type "Node", variable has type "IdentifiedNode")
    for subject in store.subjects():  # type: ignore[assignment]
        if (None, None, subject) in store:
            if (subject, None, subject) in store:
                self.subject(subject, 1)
        else:
            self.subject(subject, 1)

    # write out anything that has not yet been reached
    # write out BNodes last (to ensure they can be inlined where possible)
    bnodes = set()

    # type error: Incompatible types in assignment (expression has type "Node", variable has type "IdentifiedNode")
    for subject in store.subjects():  # type: ignore[assignment]
        if isinstance(subject, BNode):
            bnodes.add(subject)
            continue
        self.subject(subject, 1)

    # now serialize only those BNodes that have not been serialized yet
    for bnode in bnodes:
        if bnode not in self.__serialized:
            self.subject(subject, 1)

    writer.pop(RDFVOC.RDF)
    stream.write("\n".encode("latin-1"))

    # Set to None so that the memory can get garbage collected.
    self.__serialized = None  # type: ignore[assignment]
