# Context shim (see meta.json): the helpers that `_parse_single_property_shape`
# calls, copied verbatim from lazlop/semantic_objects@243c5efd8c so the region
# executes outside the package. Identical bindings for both representations.
#
#   - SH                         src/semantic_objects/namespaces.py (line 36)
#   - local_name, field_name_*   src/semantic_objects/ingest/naming.py (the
#                                helpers they need come along)
#   - ComplexConstraintIR, PinIR, PropertyShapeIR
#                                src/semantic_objects/ingest/ir.py (verbatim)
#   - _literal_str ... _parse_alternation_property_shape
#                                src/semantic_objects/ingest/shacl.py, lines
#                                1-241, i.e. everything above the region
#                                (_ALTERNATION_PREDICATES included)
from typing import List, Optional, Tuple, Union

from rdflib import BNode, Graph, RDF, URIRef, Namespace
from rdflib.collection import Collection
from rdflib.namespace import RDFS

SH = Namespace("http://www.w3.org/ns/shacl#")

# ---- ingest/naming.py ------------------------------------------------------
import keyword
import re

_CAMEL_BOUNDARY = re.compile(r'(?<!^)(?=[A-Z])')
_NON_IDENT = re.compile(r'[^0-9a-zA-Z_]')


def _avoid_keyword(name: str) -> str:
    return f"{name}_" if keyword.iskeyword(name) else name


def local_name(iri) -> str:
    """Local name of an IRI: text after the last '#' or '/'."""
    s = str(iri)
    if '#' in s:
        return s.rsplit('#', 1)[-1]
    return s.rstrip('/').rsplit('/', 1)[-1]


def snake_case(name: str) -> str:
    name = name.replace('-', '_')
    name = _CAMEL_BOUNDARY.sub('_', name)
    name = re.sub(r'_+', '_', name)
    return name.lower()


def strip_has_is_prefix(local: str) -> str:
    """hasConnectionPoint -> ConnectionPoint, isDeltaQuantity -> DeltaQuantity."""
    if local.startswith('has') and len(local) > 3 and local[3].isupper():
        return local[3:]
    if local.startswith('is') and len(local) > 2 and local[2].isupper():
        return local[2:]
    return local


def field_name_for_path(path_local: str) -> str:
    return _avoid_keyword(snake_case(strip_has_is_prefix(path_local)))


def field_name_for_qualified(target_local: str) -> str:
    """OutletConnectionPoint -> outlet_connection_point; Fluid-Water -> water."""
    simple = target_local.rsplit('-', 1)[-1] if '-' in target_local else target_local
    return _avoid_keyword(snake_case(simple))


def class_name_for(local: str) -> str:
    """Ontology local name -> Python class name.

    Taxonomy leaves are IRI'd as "Category-Value" (e.g. "Aspect-Setpoint",
    "Fluid-Water"); the trailing segment is the conventional short Python name.
    Ordinary classes have no hyphen and pass through unchanged.
    """
    candidate = local.rsplit('-', 1)[-1] if '-' in local else local
    candidate = _NON_IDENT.sub('_', candidate)
    if not candidate:
        candidate = _NON_IDENT.sub('_', local)
    if candidate[0].isdigit():
        candidate = f"_{candidate}"
    return _avoid_keyword(candidate)


def make_unique(name: str, taken: set) -> str:
    if name not in taken:
        taken.add(name)
        return name
    i = 2
    while f"{name}_{i}" in taken:
        i += 1
    unique = f"{name}_{i}"
    taken.add(unique)
    return unique

# ---- ingest/ir.py ----------------------------------------------------------
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ComplexConstraintIR:
    """A SHACL constraint that can't be represented as a single typed field."""
    path_local: Optional[str]
    kind: str  # 'sparql' | 'or' | 'nested-node' | 'inverse-path' | 'forbidden' | 'other'
    comment: Optional[str]
    message: Optional[str]
    severity: Optional[str]
    raw_turtle: str


@dataclass
class PinIR:
    """A single-valued nested constraint riding inside a qualified value
    shape's sh:node (e.g. "hasMedium must be Fluid-Water"). Captured
    separately from ComplexConstraintIR so codegen can synthesize a real
    pinned intermediate class instead of only recording raw turtle."""
    path_local: str
    target_class_local: Optional[str] = None  # from sh:class
    hasvalue_local: Optional[str] = None  # from sh:hasValue
    # from a nested sh:or/sh:xone of sh:class-only members (e.g. "hasMedium
    # must be Fluid-Water, Constituent-Refrigerant, or Fluid-Oil") - not a
    # single fixed value, so synth.py builds a narrowed Union field for this
    # one instead of a fixed-value pin. Exactly one of the three fields on
    # this class is ever set.
    or_target_locals: Optional[List[str]] = None


@dataclass
class PropertyShapeIR:
    """A SHACL property shape that maps to one required_field()/optional_field()."""
    path_local: str
    field_name: str
    target_class_local: Optional[str]
    datatype_local: Optional[str]
    min_count: Optional[int]
    max_count: Optional[int]
    qualified: bool
    comment: Optional[str]
    message: Optional[str]
    supplementary_notes: List[ComplexConstraintIR] = field(default_factory=list)
    # Nested single-value constraints from a qualifiedValueShape's sh:node
    # (e.g. a medium pin) that reduce cleanly enough to synthesize an
    # intermediate class from, rather than being discarded to a raw note.
    nested_pins: List[PinIR] = field(default_factory=list)
    # Set when this shape came from sh:or/sh:xone across alternative classes
    # sharing one path - each branch is a full nested shape (parsed the same
    # way as a top-level shape, so it may itself carry nested_pins). Renders
    # as a Union[...] field; empty for an ordinary (non-alternative) shape.
    or_branches: List['PropertyShapeIR'] = field(default_factory=list)
    # Which SHACL pattern or_branches round-trips as - these are structurally
    # different shapes, not just two ways of writing the same thing:
    # 'property' = sh:property [ sh:path P ; sh:or ( [sh:class A] [sh:class B] ) ]
    #   (bare value-shape alternatives riding one property shape's path)
    # 'class' = NodeShape sh:or ( [sh:property [...]] [sh:property [...]] )
    #   (alternative *whole* qualified property shapes, e.g. Battery's
    #   Outlet-or-Bidirectional connection point, each independently counted)
    or_scope: Optional[str] = None
    # Set only on a synthesized intermediate class's own per-pin shape ('class'
    # -> sh:class, 'value' -> sh:hasValue), or on a synthesized class's own
    # narrowed alternation field ('or' -> a real required_field() whose type
    # is narrowed to Union[...], not a fixed-value pin at all). None for an
    # ordinary shape.
    pin_kind: Optional[str] = None


@dataclass
class ClassIR:
    iri: str
    local_name: str
    class_name: str
    label: Optional[str]
    comment: Optional[str]
    parent_local_names: List[str]
    is_abstract: bool
    is_enumeration_value: bool
    bucket: str  # 'entities' | 'properties' | 'enumerationkinds'
    property_shapes: List[PropertyShapeIR] = field(default_factory=list)
    complex_constraints: List[ComplexConstraintIR] = field(default_factory=list)
    # Set on a synthesized intermediate class (one that pins/narrows a nested
    # field, e.g. OutletConnectionPoint_Water pinning `medium`): the
    # local_name of the real ontology class this stands in for. Renders as a
    # Python-level `_semantic_type = <that class>` so the class is never
    # itself asserted as an rdf:type when referenced as a field's type - same
    # convenience pattern `s223.properties.Area._semantic_type` already uses
    # by hand.
    semantic_type_local: Optional[str] = None


@dataclass
class RelationIR:
    iri: str
    local_name: str
    class_name: str
    label: Optional[str]
    comment: Optional[str]
    kind: str  # 'Relation' | 'RelationWithInverse' | 'SymmetricRelation'
    inverse_of_local: Optional[str]


@dataclass
class OntologyIR:
    classes: Dict[str, ClassIR] = field(default_factory=dict)      # keyed by local_name
    relations: Dict[str, RelationIR] = field(default_factory=dict)  # keyed by local_name
    quantitykinds_referenced: Set[str] = field(default_factory=set)
    # Intermediate pinned classes synthesized while parsing property shapes
    # (see PropertyShapeIR.nested_pins) - merged into `classes` (same bucket
    # as their base target class) before emission; kept separate here only so
    # the parser can dedupe synthesis across classes before merging.
    synthesized_classes: Dict[str, ClassIR] = field(default_factory=dict)
    source_meta: dict = field(default_factory=dict)

# ---- ingest/shacl.py, above the region -------------------------------------
# sh:or and sh:xone aren't distinguished for typing purposes - Python's type
# system has no "exactly one of" vs "at least one of" distinction, and the
# cardinality itself is still carried separately via min_count/qualifiedMinCount.
_ALTERNATION_PREDICATES = (SH['or'], SH.xone)


def _literal_str(g: Graph, subject, predicate) -> Optional[str]:
    val = g.value(subject, predicate)
    return str(val) if val is not None else None


def _literal_int(g: Graph, subject, predicate) -> Optional[int]:
    val = g.value(subject, predicate)
    return int(val) if val is not None else None


def _dump_subgraph(g: Graph, bn) -> str:
    """Best-effort serialization of a blank node's reachable subgraph, for the raw_shapes sidecar."""
    sub = Graph()
    seen = set()
    frontier = [bn]
    while frontier:
        node = frontier.pop()
        if node in seen:
            continue
        seen.add(node)
        for p, o in g.predicate_objects(node):
            sub.add((node, p, o))
            if isinstance(o, BNode) and o not in seen:
                frontier.append(o)
    try:
        return sub.serialize(format='turtle')
    except Exception:
        return ''


def _rdf_list(g: Graph, node) -> List:
    """Materialize a SHACL/RDF list (rdf:first/rdf:rest chain) into a plain list."""
    if node is None:
        return []
    return list(Collection(g, node))


def _iter_alternations(g: Graph, node):
    """Yield (list_node, predicate) for each of sh:or/sh:xone directly on
    node - ordinarily at most one, but nothing stops a shape from carrying
    both, so every caller either takes the first match or (for the
    class-level case) genuinely wants both checked independently."""
    for pred in _ALTERNATION_PREDICATES:
        val = g.value(node, pred)
        if val is not None:
            yield val, pred


def _parse_pin(g: Graph, prop_bn) -> Optional[PinIR]:
    """One sh:property bnode nested inside a value shape's sh:node, reduced to
    a PinIR if it's a clean single-valued constraint (one path, exactly one of
    sh:class/sh:hasValue/a class-only sh:or-sh:xone, nothing else) - None if
    it doesn't reduce cleanly, so the caller keeps today's raw-turtle
    fallback instead of guessing."""
    path_obj = g.value(prop_bn, SH.path)
    if path_obj is None or isinstance(path_obj, BNode):
        return None
    extra = ({p for p, _ in g.predicate_objects(prop_bn)}
             - {SH.path, SH['class'], SH.hasValue, RDFS.comment, RDFS.label})
    # sh:minCount 1 + sh:maxCount 1 *together* is redundant with, not a change
    # to, a single fixed-value pin's inherent cardinality - some ontologies
    # write it explicitly (e.g. g36's own annotation shapes on Zone/Fan/etc.).
    # Require *both* bounds, both exactly 1 - not a lone sh:minCount 1, which
    # asserts only "at least one" and shows up on a genuinely different
    # pattern (e.g. AirHeatExchanger's `pairedConnectionPoint sh:minCount 1`,
    # a relational "must be paired with some instance of this class"
    # constraint, not a fixed pin - conflating the two would silently mis-pin
    # a class reference as if it were a literal fixed value).
    min_val = g.value(prop_bn, SH.minCount)
    max_val = g.value(prop_bn, SH.maxCount)
    if min_val is not None and max_val is not None and int(min_val) == 1 and int(max_val) == 1:
        extra.discard(SH.minCount)
        extra.discard(SH.maxCount)
    found = next(_iter_alternations(g, prop_bn), None)
    alt_list = found[0] if found is not None else None
    if found is not None:
        extra.discard(found[1])
    if extra:
        return None
    target_class = g.value(prop_bn, SH['class'])
    has_value = g.value(prop_bn, SH.hasValue)
    if alt_list is not None and target_class is None and has_value is None:
        # A nested pin whose path must be one of several classes (e.g.
        # "hasMedium must be Fluid-Water, Constituent-Refrigerant, or
        # Fluid-Oil") - only reduces cleanly if every member is a bare
        # sh:class-only bnode, mirroring _parse_value_shape's own strictness.
        members = _rdf_list(g, alt_list)
        if len(members) < 2:
            return None
        targets = []
        for member in members:
            member_class = g.value(member, SH['class'])
            member_extra = {p for p, _ in g.predicate_objects(member)} - {SH['class']}
            if member_class is None or member_extra:
                return None
            targets.append(local_name(member_class))
        return PinIR(path_local=local_name(path_obj), or_target_locals=targets)
    if target_class is not None and has_value is None:
        return PinIR(path_local=local_name(path_obj), target_class_local=local_name(target_class))
    if has_value is not None and target_class is None and isinstance(has_value, URIRef):
        return PinIR(path_local=local_name(path_obj), hasvalue_local=local_name(has_value))
    return None


def _parse_nested_pins(g: Graph, value_shape_bn) -> Optional[List[PinIR]]:
    """A value shape's sh:node, reduced to PinIRs. Returns `[]` if there's no
    sh:node at all (nothing to model, fine), `None` if sh:node is present but
    contains something that doesn't reduce cleanly (caller must keep the raw
    fallback instead), or the list of pins otherwise."""
    node = g.value(value_shape_bn, SH.node)
    if node is None:
        return []
    props = list(g.objects(node, SH.property))
    if not props:
        return None
    node_extra = {p for p, _ in g.predicate_objects(node)} - {SH.property, RDF.type, RDFS.comment, RDFS.label}
    if node_extra:
        return None
    pins = []
    for prop_bn in props:
        pin = _parse_pin(g, prop_bn)
        if pin is None:
            return None
        pins.append(pin)
    return pins


def _parse_value_shape(g: Graph, value_bn, path_local: str) -> Optional[PropertyShapeIR]:
    """A bare value-shape bnode with no sh:path of its own (the path comes
    from the property shape it rides along, e.g. one member of a
    property-shape-level sh:or/xone list) - the same "sh:class + optional
    sh:node pins" shape a qualifiedValueShape has. None if it doesn't reduce
    to a clean class-anchored shape."""
    target_class = g.value(value_bn, SH['class'])
    if target_class is None:
        return None
    extra = {p for p, _ in g.predicate_objects(value_bn)} - {SH['class'], SH.node}
    if extra:
        return None
    target_local = local_name(target_class)
    branch = PropertyShapeIR(
        path_local=path_local,
        field_name=field_name_for_qualified(target_local),
        target_class_local=target_local, datatype_local=None,
        min_count=1, max_count=None, qualified=True,
        comment=None, message=None,
    )
    if (value_bn, SH.node, None) in g:
        pins = _parse_nested_pins(g, value_bn)
        if pins is None:
            return None
        branch.nested_pins = pins
    return branch


def _parse_or_members(g: Graph, alt_list, path_local: str) -> Optional[List[PropertyShapeIR]]:
    """An sh:or/sh:xone RDF list's members, each parsed via _parse_value_shape
    into a full branch shape - shared by a bare property-shape-level
    alternation and one sitting directly inside a qualifiedValueShape (no
    sh:class of its own). None (all-or-nothing) if any member doesn't reduce
    cleanly, or if there are fewer than two members."""
    members = _rdf_list(g, alt_list)
    if len(members) < 2:
        return None
    branches = []
    for member in members:
        branch = _parse_value_shape(g, member, path_local)
        if branch is None:
            return None
        branches.append(branch)
    return branches


def _or_property_shape(
    path_local: str, branches: List[PropertyShapeIR], min_count: Optional[int],
    max_count: Optional[int], qualified: bool, comment: Optional[str], message: Optional[str],
) -> PropertyShapeIR:
    """A property-scope sh:or/sh:xone reduced to a Union-typed field - shared
    by a bare property-shape-level alternation and one riding inside an
    otherwise-classless sh:qualifiedValueShape; they differ only in how
    min_count/max_count/qualified are derived from their surrounding shape."""
    shape = PropertyShapeIR(
        path_local=path_local,
        field_name=field_name_for_path(path_local),
        target_class_local=None, datatype_local=None,
        min_count=min_count, max_count=max_count, qualified=qualified,
        comment=comment, message=message,
    )
    shape.or_branches = branches
    shape.or_scope = 'property'
    return shape


def _parse_alternation_property_shape(
    g: Graph, bn, path_local: str, comment: Optional[str], message: Optional[str]
) -> Optional[PropertyShapeIR]:
    """Property-shape-level sh:or/sh:xone: `sh:property [ sh:path P ; sh:or
    ( [sh:class A] [sh:class B] ... ) ]`. Reduces to a Union-typed field only
    if every alternative resolves to a clean class-anchored shape; None
    otherwise (caller falls back to today's raw complex constraint)."""
    found = next(_iter_alternations(g, bn), None)
    if found is None:
        return None
    alt_list, _ = found
    branches = _parse_or_members(g, alt_list, path_local)
    if branches is None:
        return None
    qmin = _literal_int(g, bn, SH.qualifiedMinCount)
    min_count = _literal_int(g, bn, SH.minCount)
    max_count = _literal_int(g, bn, SH.maxCount)
    # Honest, not assumed: a bare property-shape-level sh:or (no
    # qualifiedMinCount - that's an sh:qualifiedValueShape-specific concept
    # this pattern doesn't use) has no inherent cardinality of its own, e.g.
    # s223:Equipment.contains is an sh:or with *no* count at all ("zero or
    # more" per its own comment) - forcing qualified=True here previously
    # made every such field a mandatory constructor argument. Let the
    # existing is_dedicated_field rule (qualified or min_count>=1) decide,
    # exactly as it does for an ordinary (non-alternation) shape.
    return _or_property_shape(
        path_local, branches,
        min_count=qmin if qmin is not None else min_count, max_count=max_count,
        qualified=(qmin is not None), comment=comment, message=message,
    )


