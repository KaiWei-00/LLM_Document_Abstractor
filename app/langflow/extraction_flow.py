from typing import Dict, Any, List, Callable
import os
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
import json


def create_extraction_nodes():
    """
    Create the nodes for the LangGraph extraction flow.
    
    Returns:
        Dict containing the flow nodes
    """
    # Initialize the LLM
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
    llm = ChatOpenAI(api_key=api_key, model=model_name)
    
    # Create document preprocessing node
    def preprocess_document(state: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare the document text for extraction."""
        text = state["document_text"]
        
        # Truncate if text is too long (avoid token limits)
        max_tokens = 8000  # Conservative limit for context
        if len(text) > max_tokens * 4:  # Rough character to token ratio
            text = text[:max_tokens * 4] + "\n[Document truncated due to length]"
        
        # Basic cleaning
        text = text.replace("\x00", "")  # Remove null bytes
        
        # Update state
        state["processed_text"] = text
        return state
    
    # Create schema preparation node
    def prepare_schema_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
        """Format the schema for the extraction prompt."""
        schema = state["schema"]
        
        # Format schema into a string representation for the prompt
        schema_str = json.dumps(schema, indent=2)
        
        state["schema_prompt"] = schema_str
        return state
    
    # Create extraction prompt template
    extraction_template = """
    You are a document information extraction expert. Your task is to extract structured information from the document text according to the specified schema.
    
    # Document Text:
    {processed_text}
    
    # Target Schema:
    {schema_prompt}
    
    # Instructions:
    1. Extract all fields defined in the schema from the document.
    2. For each field, provide the exact value found in the document.
    3. Maintain the correct data type for each field as defined in the schema.
    4. If a field cannot be found in the document, use null for that field.
    5. Return ONLY a valid JSON object matching the schema, nothing else.
    
    # Extracted JSON (ensure valid JSON format):
    """
    
    extraction_prompt = ChatPromptTemplate.from_template(extraction_template)
    
    # Create LLM extraction node
    def extract_with_llm(state: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to extract structured data according to schema."""
        # Prepare the chain
        chain = (
            {"processed_text": RunnablePassthrough(), "schema_prompt": RunnablePassthrough()}
            | extraction_prompt
            | llm
        )
        
        # Run the extraction
        response = chain.invoke({
            "processed_text": state["processed_text"], 
            "schema_prompt": state["schema_prompt"]
        })
        
        # Extract the JSON from the response
        result_text = response.content
        
        try:
            # Extract JSON from the response if needed
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].strip()
            else:
                json_str = result_text.strip()
                
            extracted_data = json.loads(json_str)
            state["extraction_result"] = extracted_data
        except Exception as e:
            state["error"] = f"Failed to parse LLM response as JSON: {str(e)}"
            state["extraction_result"] = {"error": "Failed to extract structured data"}
        
        return state
    
    # Create validation node
    def validate_extraction(state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the extracted data against the schema."""
        if "error" in state:
            return state
            
        schema = state["schema"]
        extracted_data = state["extraction_result"]
        
        # Check if all required fields from schema are present
        for field, field_type in schema.items():
            if field not in extracted_data:
                # Add missing fields as null
                extracted_data[field] = None
            else:
                # Validate type and convert if necessary
                value = extracted_data[field]
                if value is not None:  # Skip null values
                    if field_type == "number" and isinstance(value, str):
                        # Try to convert string to number
                        try:
                            extracted_data[field] = float(value)
                            # Convert to int if it's a whole number
                            if extracted_data[field].is_integer():
                                extracted_data[field] = int(extracted_data[field])
                        except:
                            pass  # Keep as is if conversion fails
        
        state["extraction_result"] = extracted_data
        return state
    
    return {
        "preprocess_document": preprocess_document,
        "prepare_schema_prompt": prepare_schema_prompt,
        "extract_with_llm": extract_with_llm,
        "validate_extraction": validate_extraction
    }


def build_extraction_graph() -> StateGraph:
    """
    Build the LangGraph extraction flow.
    
    Returns:
        StateGraph: The constructed flow graph
    """
    # Define the state schema
    state_schema = {
        "document_text": str,
        "schema": dict,
        "processed_text": str,
        "schema_prompt": str,
        "extraction_result": dict,
        "error": str
    }
    
    # Create a new graph
    graph = StateGraph(state_schema)
    
    # Get nodes
    nodes = create_extraction_nodes()
    
    # Add nodes to the graph
    graph.add_node("preprocess_document", nodes["preprocess_document"])
    graph.add_node("prepare_schema_prompt", nodes["prepare_schema_prompt"])
    graph.add_node("extract_with_llm", nodes["extract_with_llm"])
    graph.add_node("validate_extraction", nodes["validate_extraction"])
    
    # Define the edges
    graph.add_edge("preprocess_document", "prepare_schema_prompt")
    graph.add_edge("prepare_schema_prompt", "extract_with_llm")
    graph.add_edge("extract_with_llm", "validate_extraction")
    
    # Set the entry point
    graph.set_entry_point("preprocess_document")
    
    # Compile the graph
    return graph.compile()


def run_extraction_flow(document_text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the extraction flow on a document with the given schema.
    
    Args:
        document_text: Text extracted from the document
        schema: Data schema to extract
    
    Returns:
        Dict containing the extracted data
    """
    # Build the graph
    graph = build_extraction_graph()
    
    # Prepare initial state
    initial_state = {
        "document_text": document_text,
        "schema": schema,
        "processed_text": "",
        "schema_prompt": "",
        "extraction_result": {},
        "error": None
    }
    
    # Execute the graph
    try:
        result = graph.invoke(initial_state)
        
        # Return the extraction result
        if "error" in result and result["error"]:
            return {"error": result["error"]}
        else:
            return result["extraction_result"]
    except Exception as e:
        return {"error": f"Extraction flow failed: {str(e)}"}
