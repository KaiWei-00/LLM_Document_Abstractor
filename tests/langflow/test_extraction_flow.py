import pytest
from unittest.mock import patch, MagicMock
import json
import os

from app.langflow.extraction_flow import (
    create_extraction_nodes,
    build_extraction_graph,
    run_extraction_flow
)


@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    return {
        "name": "string",
        "age": "number",
        "email": "string",
        "is_active": "boolean"
    }


@pytest.fixture
def sample_document_text():
    """Create a sample document text for testing."""
    return """
    Personal Information Form
    
    Name: John Doe
    Age: 35
    Email: john.doe@example.com
    Status: Active
    
    Additional Notes: None
    """


@patch('os.getenv')
@patch('langchain_openai.ChatOpenAI')
def test_create_extraction_nodes(mock_chat_openai, mock_getenv):
    """Test creation of extraction nodes."""
    # Setup mocks
    mock_getenv.side_effect = lambda key, default=None: {
        "OPENAI_API_KEY": "fake-api-key", 
        "OPENAI_MODEL_NAME": "gpt-4"
    }.get(key, default)
    
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm
    
    # Call the function
    nodes = create_extraction_nodes()
    
    # Verify the nodes were created
    assert "preprocess_document" in nodes
    assert "prepare_schema_prompt" in nodes
    assert "extract_with_llm" in nodes
    assert "validate_extraction" in nodes
    
    # Test the behavior of individual nodes
    
    # Test preprocess_document
    state = {"document_text": "Test document"}
    result = nodes["preprocess_document"](state)
    assert "processed_text" in result
    assert result["processed_text"] == "Test document"
    
    # Test prepare_schema_prompt
    state = {"schema": {"name": "string", "age": "number"}}
    result = nodes["prepare_schema_prompt"](state)
    assert "schema_prompt" in result
    # The schema should be converted to a formatted JSON string
    assert "{" in result["schema_prompt"]
    assert "name" in result["schema_prompt"]


@patch('os.getenv')
def test_build_extraction_graph(mock_getenv):
    """Test building the extraction graph."""
    # Setup mock
    mock_getenv.return_value = "fake-api-key"
    
    # Call the function
    graph = build_extraction_graph()
    
    # Verify the graph was built
    assert graph is not None


@patch('app.langflow.extraction_flow.build_extraction_graph')
def test_run_extraction_flow_success(mock_build_graph, sample_schema, sample_document_text):
    """Test successful extraction flow execution."""
    # Create mock graph result
    expected_result = {
        "name": "John Doe",
        "age": 35,
        "email": "john.doe@example.com",
        "is_active": True
    }
    
    # Setup mock graph
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "extraction_result": expected_result,
        "error": None
    }
    mock_build_graph.return_value = mock_graph
    
    # Call the function
    result = run_extraction_flow(sample_document_text, sample_schema)
    
    # Verify expectations
    mock_build_graph.assert_called_once()
    mock_graph.invoke.assert_called_once()
    assert result == expected_result


@patch('app.langflow.extraction_flow.build_extraction_graph')
def test_run_extraction_flow_error(mock_build_graph, sample_schema, sample_document_text):
    """Test handling of extraction flow error."""
    # Setup mock graph to return error
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "extraction_result": {},
        "error": "LLM processing error"
    }
    mock_build_graph.return_value = mock_graph
    
    # Call the function
    result = run_extraction_flow(sample_document_text, sample_schema)
    
    # Verify error handling
    assert "error" in result
    assert result["error"] == "LLM processing error"


@patch('app.langflow.extraction_flow.build_extraction_graph')
def test_run_extraction_flow_exception(mock_build_graph, sample_schema, sample_document_text):
    """Test handling of extraction flow exception."""
    # Setup mock graph to raise exception
    mock_graph = MagicMock()
    mock_graph.invoke.side_effect = Exception("Graph execution failed")
    mock_build_graph.return_value = mock_graph
    
    # Call the function
    result = run_extraction_flow(sample_document_text, sample_schema)
    
    # Verify exception handling
    assert "error" in result
    assert "Extraction flow failed" in result["error"]
    assert "Graph execution failed" in result["error"]


@patch('app.langflow.extraction_flow.build_extraction_graph')
def test_run_extraction_flow_missing_fields(mock_build_graph, sample_schema, sample_document_text):
    """Test handling of missing fields in extraction result."""
    # Create mock extraction result with missing fields
    partial_result = {
        "name": "John Doe",
        "age": 35,
        # email and is_active are missing
    }
    
    # Setup validate_extraction to add missing fields
    def mock_validate(state):
        extracted = state["extraction_result"]
        schema = state["schema"]
        
        # Add missing fields as null
        for field in schema:
            if field not in extracted:
                extracted[field] = None
        
        state["extraction_result"] = extracted
        return state
    
    # Setup mock nodes and graph
    mock_nodes = {
        "preprocess_document": lambda s: s,
        "prepare_schema_prompt": lambda s: s,
        "extract_with_llm": lambda s: {**s, "extraction_result": partial_result},
        "validate_extraction": mock_validate
    }
    
    mock_create_nodes = MagicMock(return_value=mock_nodes)
    
    with patch('app.langflow.extraction_flow.create_extraction_nodes', mock_create_nodes):
        # Build a real graph with our mock nodes
        graph = build_extraction_graph()
        mock_build_graph.return_value = graph
        
        # Run the extraction
        result = run_extraction_flow(sample_document_text, sample_schema)
        
        # Verify fields were added with null values
        assert result["name"] == "John Doe"
        assert result["age"] == 35
        assert "email" in result
        assert result["email"] is None
        assert "is_active" in result
        assert result["is_active"] is None


@patch('app.langflow.extraction_flow.build_extraction_graph')
def test_run_extraction_flow_type_conversion(mock_build_graph, sample_schema):
    """Test type conversion in extraction flow."""
    # Create mock extraction result with string instead of number
    result_with_wrong_types = {
        "name": "John Doe",
        "age": "35",  # String instead of number
        "email": "john.doe@example.com",
        "is_active": "true"  # String instead of boolean
    }
    
    # Setup validate_extraction to convert types
    def mock_validate(state):
        extracted = state["extraction_result"]
        schema = state["schema"]
        
        # Convert types as needed
        for field, field_type in schema.items():
            if field in extracted and extracted[field] is not None:
                if field_type == "number" and isinstance(extracted[field], str):
                    try:
                        num = float(extracted[field])
                        if num.is_integer():
                            extracted[field] = int(num)
                        else:
                            extracted[field] = num
                    except:
                        pass
        
        state["extraction_result"] = extracted
        return state
    
    # Setup mock nodes and graph
    mock_nodes = {
        "preprocess_document": lambda s: s,
        "prepare_schema_prompt": lambda s: s,
        "extract_with_llm": lambda s: {**s, "extraction_result": result_with_wrong_types},
        "validate_extraction": mock_validate
    }
    
    mock_create_nodes = MagicMock(return_value=mock_nodes)
    
    with patch('app.langflow.extraction_flow.create_extraction_nodes', mock_create_nodes):
        # Build a real graph with our mock nodes
        graph = build_extraction_graph()
        mock_build_graph.return_value = graph
        
        # Run the extraction
        document_text = "Sample text"
        result = run_extraction_flow(document_text, sample_schema)
        
        # Verify type conversion
        assert result["name"] == "John Doe"
        assert result["age"] == 35  # Converted to int
        assert isinstance(result["age"], int)
        assert result["email"] == "john.doe@example.com"
