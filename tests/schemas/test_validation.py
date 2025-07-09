import pytest
from app.schemas.validation import validate_schema


def test_valid_schema():
    """Test that a valid schema passes validation."""
    schema = {
        "name": "string",
        "age": "number",
        "is_active": "boolean",
        "address": "object",
        "tags": "array",
        "birth_date": "date"
    }
    
    # Should not raise any exception
    validate_schema(schema)


def test_empty_schema():
    """Test that an empty schema raises ValueError."""
    with pytest.raises(ValueError) as excinfo:
        validate_schema({})
    
    assert "Schema cannot be empty" in str(excinfo.value)


def test_none_schema():
    """Test that None as schema raises ValueError."""
    with pytest.raises(ValueError) as excinfo:
        validate_schema(None)
    
    assert "Schema must be a dictionary" in str(excinfo.value)


def test_invalid_schema_type():
    """Test that non-dict schema raises ValueError."""
    with pytest.raises(ValueError) as excinfo:
        validate_schema("not a dict")
    
    assert "Schema must be a dictionary" in str(excinfo.value)


def test_invalid_field_name():
    """Test that invalid field names raise ValueError."""
    schema = {
        "valid_name": "string",
        "": "number",  # Empty string as field name
        123: "boolean"  # Non-string as field name
    }
    
    with pytest.raises(ValueError) as excinfo:
        validate_schema(schema)
    
    assert "Field name must be a non-empty string" in str(excinfo.value)


def test_invalid_field_type():
    """Test that invalid field types raise ValueError."""
    schema = {
        "name": "string",
        "age": "integer",  # Not in valid_types
        "active": "bool"   # Not in valid_types
    }
    
    with pytest.raises(ValueError) as excinfo:
        validate_schema(schema)
    
    assert "has invalid type" in str(excinfo.value)
    assert "Supported types are:" in str(excinfo.value)
