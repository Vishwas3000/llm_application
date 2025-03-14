from typing import Dict, Any, List, Optional, Tuple, Callable
import logging
from utils.helpers import calculator
from utils.csv_loader import CSVLoader

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for agent tools that can be called."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Callable] = {}
        self.csv_loader: Optional[CSVLoader] = None
        logger.info("Initialized tool registry")
    
    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function.
        
        Args:
            name: Name of the tool
            func: Function implementing the tool
        """
        self.tools[name] = func
        logger.info(f"Registered tool: {name}")
    
    def set_csv_loader(self, csv_loader: CSVLoader) -> None:
        """
        Set the CSV loader for use by tools.
        
        Args:
            csv_loader: The CSV loader instance
        """
        self.csv_loader = csv_loader
        logger.info("Set CSV loader in tool registry")
    
    async def execute_tool(self, tool_name: str, tool_input: str) -> Tuple[Any, str]:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool
            
        Returns:
            Tuple of (result, description)
        """
        # Normalize tool name
        normalized_name = tool_name.lower().replace(" ", "_")
        
        for name in self.tools:
            if name.lower().replace(" ", "_") == normalized_name:
                try:
                    logger.info(f"Executing tool: {name} with input: {tool_input[:100]}...")
                    result = self.tools[name](tool_input)
                    return result, f"Successfully executed tool: {name}"
                except Exception as e:
                    error_msg = f"Error executing tool {name}: {str(e)}"
                    logger.error(error_msg)
                    return None, error_msg
        
        error_msg = f"Tool not found: {tool_name}"
        logger.warning(error_msg)
        return None, error_msg

# Define standard tools
def create_standard_tools() -> ToolRegistry:
    """
    Create and register standard tools.
    
    Returns:
        ToolRegistry with standard tools registered
    """
    registry = ToolRegistry()
    
    # Calculator tool
    def calculator_tool(expression: str) -> Dict[str, Any]:
        return {
            "result": calculator(expression),
            "expression": expression
        }
    registry.register_tool("Calculator", calculator_tool)
    
    # Query Database tool (simulated for CSV)
    def query_database_tool(query: str) -> Dict[str, Any]:
        if not registry.csv_loader or registry.csv_loader.df is None:
            return {
                "error": "No CSV data loaded or database not available"
            }
        
        # In a real application, this would connect to a database
        # Here we'll simulate basic SQL-like operations on the DataFrame
        try:
            # Very simplified SQL parsing - just for demonstration
            query = query.lower()
            
            # Extract column names after SELECT
            if "select" in query and "from" in query:
                select_part = query.split("from")[0].replace("select", "").strip()
                columns = [col.strip() for col in select_part.split(",")]
                
                # Check for aggregations
                agg_funcs = ["count", "sum", "avg", "min", "max"]
                has_agg = any(func + "(" in select_part for func in agg_funcs)
                
                # Check for WHERE clause
                where_clause = None
                if "where" in query:
                    where_part = query.split("where")[1].strip()
                    where_clause = where_part
                
                # Very simple implementation - in a real app you'd want a proper SQL parser
                df = registry.csv_loader.df
                
                # Apply WHERE filtering if needed
                if where_clause:
                    # This is a very simplified approach
                    # In a real application, you'd want to use a proper parser
                    for column in df.columns:
                        if column in where_clause:
                            # Look for simple equality conditions
                            if f"{column} =" in where_clause or f"{column}=" in where_clause:
                                # Extract value after equals sign
                                value_str = where_clause.split("=")[1].strip()
                                if value_str.startswith("'") and value_str.endswith("'"):
                                    value = value_str[1:-1]  # Remove quotes
                                else:
                                    try:
                                        value = float(value_str)
                                    except:
                                        value = value_str
                                        
                                # Filter dataframe
                                df = df[df[column] == value]
                
                # Select specified columns
                if "*" not in select_part:
                    # Handle aggregations
                    if has_agg:
                        result = {}
                        for col_expr in columns:
                            for func in agg_funcs:
                                if func + "(" in col_expr:
                                    # Extract column name from function
                                    col = col_expr.split("(")[1].split(")")[0].strip()
                                    if func == "count":
                                        result[col_expr] = len(df)
                                    elif func == "sum":
                                        result[col_expr] = df[col].sum()
                                    elif func == "avg":
                                        result[col_expr] = df[col].mean()
                                    elif func == "min":
                                        result[col_expr] = df[col].min()
                                    elif func == "max":
                                        result[col_expr] = df[col].max()
                        return result
                    else:
                        valid_cols = [col for col in columns if col in df.columns]
                        if valid_cols:
                            df = df[valid_cols]
                
                # Limit to first 50 rows for output
                result_df = df.head(50)
                
                return {
                    "query": query,
                    "result": result_df.to_dict(orient="records"),
                    "total_rows": len(df),
                    "returned_rows": len(result_df)
                }
            
            return {
                "error": "Could not parse SQL query. Please use a simple 'SELECT ... FROM ... WHERE ...' format."
            }
            
        except Exception as e:
            logger.error(f"Error executing database query: {str(e)}")
            return {"error": f"Error executing query: {str(e)}"}
    
    registry.register_tool("Query_Database", query_database_tool)
    
    # Analyze CSV tool
    def analyze_csv_tool(operation: str) -> Dict[str, Any]:
        if not registry.csv_loader or registry.csv_loader.df is None:
            return {
                "error": "No CSV data loaded"
            }
        
        try:
            result, description = registry.csv_loader.execute_pandas_operation(operation)
            return {
                "operation": operation,
                "result": result,
                "description": description
            }
        except Exception as e:
            logger.error(f"Error analyzing CSV: {str(e)}")
            return {"error": f"Error analyzing CSV: {str(e)}"}
    
    registry.register_tool("Analyze_CSV", analyze_csv_tool)
    
    # Generate Final Answer tool
    def generate_final_answer(answer: str) -> Dict[str, Any]:
        return {
            "answer": answer
        }
    
    registry.register_tool("Generate_Final_Answer", generate_final_answer)
    
    return registry