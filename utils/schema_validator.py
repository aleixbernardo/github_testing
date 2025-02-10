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
