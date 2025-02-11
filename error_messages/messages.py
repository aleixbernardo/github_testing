class ErrorMessages:
    # Authentication errors
    MISSING_TOKEN_ERROR = "Requires authentication"
    INVALID_CREDENTIALS = "Bad credentials"

    # General Errors
    NOT_FOUND = "Not Found"

    # Combination Errors
    INVALID_VISIBILITY_AFFILIATION_TYPE_COMBINATION = (
        "If you specify visibility or affiliation, you cannot specify type."
    )
