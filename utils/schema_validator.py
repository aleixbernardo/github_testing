from jsonschema import validate, ValidationError


def validate_json_schema(json_data, schema):
    """
    Validates JSON data against a given schema.

    :param json_data: dict - The JSON response data
    :param schema: dict - The JSON Schema to validate against
    :return: bool - True if valid, raises an exception if invalid
    """
    try:
        validate(instance=json_data, schema=schema)
        return True
    except ValidationError as e:
        raise AssertionError(f"JSON Schema validation failed: {e.message}")


from dataclasses import is_dataclass
from typing import Type, TypeVar, Dict, Any

T = TypeVar("T")


def from_dict(data: Dict[str, Any], dataclass_type: Type[T]) -> T:
    """Recursively converts a dictionary into a dataclass instance."""
    if not isinstance(data, dict):
        return data  # Return as-is if it's not a dictionary

    field_types = {f.name: f.type for f in dataclass_type.__dataclass_fields__.values()}

    for key, value in data.items():
        if key in field_types:
            field_type = field_types[key]

            # Handle lists of dataclasses
            if (
                isinstance(value, list)
                and hasattr(field_type, "__origin__")
                and field_type.__origin__ == list
            ):
                inner_type = field_type.__args__[0]  # Extract the list element type
                if is_dataclass(inner_type):
                    data[key] = [from_dict(item, inner_type) for item in value]

            # Handle nested dataclasses
            elif is_dataclass(field_type):
                data[key] = from_dict(value, field_type)

    return dataclass_type(**data)
