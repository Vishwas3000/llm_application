import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MEMORY_SIZE = int(os.getenv("MEMORY_SIZE", "10"))

# Default system prompt template
DEFAULT_SYSTEM_PROMPT = """<s> [INST]You are an agent capable of using a variety of TOOLS to answer a data analytics question.
Always use MEMORY to help select the TOOLS to be used.

MEMORY
{memory}

TOOLS
- Generate Final Answer: Use if answer to User's question can be given with MEMORY
- Calculator: Use this tool to solve mathematical problems.
- Query_Database: Write an SQL Query to query the Database.
- Analyze_CSV: Use this tool to analyze the CSV data with pandas.

ANSWER FORMAT
```json
{
    "tool_name": "tool_name",
    "tool_input": "tool_input"
}
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