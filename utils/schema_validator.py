from dataclasses import is_dataclass
from typing import TypeVar, Dict, Any, Type

from jsonschema import validate, ValidationError


def validate_json_schema(json_data, schema):
    """
    Validates the provided JSON data against a given JSON Schema.

    Parameters:
    - json_data (dict): The JSON data (typically a dictionary) to validate.
    - schema (dict): The JSON Schema that the data should adhere to.

    Returns:
    - bool: Returns True if the JSON data is valid according to the schema.
    - Raises an exception: If validation fails, raises a custom AssertionError with a descriptive message.
    """
    try:
        # Use the 'jsonschema' library's 'validate' function to validate the data
        validate(instance=json_data, schema=schema)
        return True  # Return True if validation is successful
    except ValidationError as e:
        # Catch any validation errors and raise a custom assertion error with the validation message
        raise AssertionError(f"JSON Schema validation failed: {e.message}")


T = TypeVar("T")


def from_dict(data: Dict[str, Any], dataclass_type: Type[T]) -> T:
    """
    Recursively converts a dictionary into a dataclass instance.

    Parameters:
    - data (Dict[str, Any]): The dictionary data to convert into a dataclass.
    - dataclass_type (Type[T]): The target dataclass type to convert the data into.

    Returns:
    - T: The converted dataclass instance.
    """
    # If data is not a dictionary, return the data as is (base case for recursion)
    if not isinstance(data, dict):
        return data

    # Extract field names and types from the dataclass
    field_types = {f.name: f.type for f in dataclass_type.__dataclass_fields__.values()}

    # Iterate through the dictionary and convert the values to the corresponding dataclass types
    for key, value in data.items():
        if key in field_types:
            field_type = field_types[key]

            # If the value is a list and the dataclass field is a list, handle that separately
            if (
                isinstance(value, list)
                and hasattr(field_type, "__origin__")
                and field_type.__origin__ == list
            ):
                inner_type = field_type.__args__[
                    0
                ]  # Get the type of the elements in the list
                if is_dataclass(inner_type):  # If the list contains dataclass instances
                    data[key] = [from_dict(item, inner_type) for item in value]

            # If the field type is a dataclass, recursively convert it to the appropriate dataclass
            elif is_dataclass(field_type):
                data[key] = from_dict(value, field_type)

    # Return an instance of the dataclass with the updated data
    return dataclass_type(**data)
