from typing import Dict, Any, List, Optional
import json

# Default system prompt template
DEFAULT_SYSTEM_PROMPT = """<s> [INST]You are an agent capable of using a variety of TOOLS to answer a data analytics question.
Always use MEMORY to help select the TOOLS to be used.

MEMORY
{memory}

TOOLS
- Generate_Final_Answer: Use if answer to User's question can be given with MEMORY
- Calculator: Use this tool to solve mathematical problems.
- Query_Database: Write an SQL Query to query the Database.
- Analyze_CSV: Use this tool to analyze the CSV data with pandas.

ANSWER FORMAT
```json
{{
    "tool_name": "tool_name",
    "tool_input": "tool_input"
}}
```
[/INST]
"""

# Tool formats
TOOL_FORMATS = {
    "Calculator": {
        "description": "Use this tool to solve mathematical problems.",
        "input_format": "A mathematical expression to evaluate.",
    },
    "Query_Database": {
        "description": "Write an SQL Query to query the Database.",
        "input_format": "An SQL query string.",
    },
    "Analyze_CSV": {
        "description": "Use this tool to analyze the CSV data with pandas.",
        "input_format": "A pandas operation or analysis to perform on the data.",
    },
    "Generate_Final_Answer": {
        "description": "Use if answer to User's question can be given with MEMORY",
        "input_format": "A detailed answer to the user's question.",
    }
}

class PromptTemplates:
    """Templates for generating prompts for the agent."""
    
    @staticmethod
    def get_system_prompt(memory_content: str) -> str:
        """
        Get the system prompt with memory content.
        
        Args:
            memory_content: The formatted memory content
            
        Returns:
            System prompt with memory
        """
        return DEFAULT_SYSTEM_PROMPT.format(memory=memory_content)
    
    @staticmethod
    def get_tool_description() -> str:
        """
        Get the description of available tools.
        
        Returns:
            Description of tools
        """
        tool_description = ["TOOLS"]
        
        for tool_name, tool_info in TOOL_FORMATS.items():
            description = tool_info.get("description", "No description available")
            tool_description.append(f"- {tool_name}: {description}")
        
        return "\n".join(tool_description)
    
    @staticmethod
    def format_tool_response(tool_name: str, tool_result: Any) -> str:
        """
        Format a tool response for the agent.
        
        Args:
            tool_name: Name of the tool
            tool_result: Result from the tool
            
        Returns:
            Formatted tool response
        """
        result_str = f"TOOL RESPONSE: {tool_name}\n"
        
        if isinstance(tool_result, dict):
            if "error" in tool_result:
                result_str += f"Error: {tool_result['error']}\n"
            else:
                for key, value in tool_result.items():
                    if key != "error":
                        if isinstance(value, (list, dict)):
                            value_str = json.dumps(value, indent=2)
                            result_str += f"{key}:\n{value_str}\n"
                        else:
                            result_str += f"{key}: {value}\n"
        else:
            result_str += str(tool_result)
        
        return result_str
    
    @staticmethod
    def format_user_question(question: str) -> str:
        """
        Format a user question for the agent.
        
        Args:
            question: The user's question
            
        Returns:
            Formatted user question
        """
        return f"User: {question}"