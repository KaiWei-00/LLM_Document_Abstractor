from typing import Dict, Any, List, Union, Set


def validate_schema(schema: Dict[str, Any]) -> None:
    """
    Validate the schema provided by the client.
    
    Args:
        schema: Dictionary representing the data schema
    
    Raises:
        ValueError: If the schema is invalid
    """
    # Check if schema is empty
    if not schema:
        raise ValueError("Schema cannot be empty")
    
    # Check that schema is a dictionary with string keys
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary with field names as keys")
    
    # Valid field types
    valid_types = {"string", "number", "boolean", "date", "array", "object"}
    
    # Check each field
    for field_name, field_type in schema.items():
        # Check field name
        if not isinstance(field_name, str) or not field_name:
            raise ValueError(f"Field name must be a non-empty string: {field_name}")
        
        # Check field type
        if not isinstance(field_type, str) or field_type.lower() not in valid_types:
            raise ValueError(
                f"Field '{field_name}' has invalid type '{field_type}'. "
                f"Supported types are: {', '.join(valid_types)}"
            )
    
    # Schema is valid
    return
