# Extracted from lazlop/semantic_objects@243c5efd8c : .claude/worktrees/watr-ingestion/src/semantic_objects/model_loader.py
# region: ModelLoader._instantiate_from_row (lines 248-360, stratum trav_single_value)
# licence of the source repository: see meta.json
from typing import Any, Dict, List, Optional, Union, Type, get_origin, get_args
from dataclasses import fields, is_dataclass, MISSING, _MISSING_TYPE
from rdflib import Graph, Literal, Namespace, URIRef
from .core import Resource, Node, NamedNode

if field_name in row.index and row[field_name] is not None:
    field_value_uri = row[field_name]
    field_type = field_obj.type

    # Handle Optional types
    origin = get_origin(field_type)
    if origin is not None:
        args = get_args(field_type)
        if args:
            field_type = args[0]

    # If field type is a Resource subclass, recursively instantiate
    if isinstance(field_type, type) and issubclass(field_type, Resource):
        # Check if it's a NamedNode (fixed value)
        if issubclass(field_type, NamedNode):
            # Just use the class itself
            kwargs[field_name] = field_type
        else:
            # Recursively instantiate the related object
            # For now, create a simple instance with just the URI
            if str(field_value_uri) in instances_cache:
                kwargs[field_name] = instances_cache[str(field_value_uri)]
            else:
                # Create a minimal instance
                try:
                    _, _, related_local_name = self.g.compute_qname(field_value_uri)
                except:
                    related_local_name = str(field_value_uri).split('#')[-1].split('/')[-1]

                # Get value if it's a property
                # Convert to URIRef if it's a string
                if isinstance(field_value_uri, str):
                    field_value_uri = URIRef(field_value_uri)

                value = self.g.value(field_value_uri, S223['hasValue'])
                unit = self.g.value(field_value_uri, QUDT['hasUnit'])

                if value is not None:
                    # It's a property with a value
                    related_kwargs = {}

                    # Check if this class has a _semantic_type attribute
                    # This indicates fields that are set at the class level and shouldn't be passed to __init__
                    has_semantic_type = hasattr(field_type, '_semantic_type') and field_type._semantic_type is not None

                    if has_semantic_type:
                        # For classes with _semantic_type, only pass instance-level fields
                        # Identify which fields are instance-level (init=True) vs class-level (init=False)
                        if hasattr(field_type, '__dataclass_fields__'):
                            for inst_field_name, inst_field_obj in field_type.__dataclass_fields__.items():
                                if inst_field_obj.init:
                                    # This is an instance-level field
                                    if inst_field_name == 'value':
                                        related_kwargs['value'] = float(value) if value else None
                                    elif inst_field_name == 'unit' and unit:
                                        # Find the Unit class for this unit
                                        try:
                                            _, _, unit_name = self.g.compute_qname(unit)
                                            # Try to import the unit class
                                            from . import units
                                            unit_class = getattr(units, unit_name, None)
                                            if unit_class:
                                                related_kwargs['unit'] = unit_class
                                        except:
                                            pass
                    else:
                        # For other Node types, include _name
                        related_kwargs['_name'] = related_local_name
                        if 'value' in [f.name for f in fields(field_type)]:
                            related_kwargs['value'] = float(value) if value else None
                        if 'unit' in [f.name for f in fields(field_type)] and unit:
                            # Find the Unit class for this unit
                            try:
                                _, _, unit_name = self.g.compute_qname(unit)
                                # Try to import the unit class
                                from . import units
                                unit_class = getattr(units, unit_name, None)
                                if unit_class:
                                    related_kwargs['unit'] = unit_class
                            except:
                                pass

                    related_instance = field_type(**related_kwargs)
                    instances_cache[str(field_value_uri)] = related_instance
                    kwargs[field_name] = related_instance
                else:
                    # No value found - check if this class requires instance-level fields
                    has_semantic_type = hasattr(field_type, '_semantic_type') and field_type._semantic_type is not None

                    # Check if there are required instance-level fields
                    has_required_instance_fields = False
                    if hasattr(field_type, '__dataclass_fields__'):
                        for inst_field_name, inst_field_obj in field_type.__dataclass_fields__.items():
                            if inst_field_obj.init and isinstance(inst_field_obj.default, _MISSING_TYPE):
                                has_required_instance_fields = True
                                break

                    if has_semantic_type and has_required_instance_fields:
                        # Can't create instance without required fields - skip this field
                        pass
                    else:
                        # Just create with name
                        related_instance = field_type(_name=related_local_name)
                        instances_cache[str(field_value_uri)] = related_instance
                        kwargs[field_name] = related_instance
    else:
        # For primitive types, extract the value
        value = self._get_field_value_from_uri(
            field_value_uri,
            field_type,
            field_obj
        )
        kwargs[field_name] = value
