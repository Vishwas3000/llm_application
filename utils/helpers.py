import logging
import json
import re
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: The logging level to use
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
        
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger.info(f"Logging configured with level: {log_level}")

def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """
    Safely parse a JSON string, handling common issues.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        The parsed JSON as a dictionary
    """
    try:
        # First, try to extract JSON if it's within a code block
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", json_str)
        if match:
            json_str = match.group(1)
        
        # Clean up any trailing commas which are invalid in JSON
        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse JSON: {json_str}")
        return {}
    except Exception as e:
        logger.error(f"Error in safe_json_loads: {str(e)}")
        return {}

def format_response_for_display(response: Any) -> str:
    """
    Format a response for display to the user.
    
    Args:
        response: The response to format
        
    Returns:
        Formatted string representation
    """
    if isinstance(response, dict):
        try:
            return json.dumps(response, indent=2)
        except:
            return str(response)
    elif isinstance(response, (list, tuple)):
        try:
            return json.dumps(response, indent=2)
        except:
            return str(response)
    else:
        return str(response)

def calculator(expression: str) -> str:
    """
    Simple calculator tool for basic math expressions.
    
    Args:
        expression: The math expression to evaluate
        
    Returns:
        String result or error message
    """
    try:
        # Remove any unsafe operations
        sanitized = re.sub(r'[^0-9+\-*/().%\s]', '', expression)
        
        # Evaluate the expression
        result = eval(sanitized)
        return f"Result: {result}"
    except Exception as e:
        logger.error(f"Calculator error: {str(e)}")
        return f"Error calculating result: {str(e)}"