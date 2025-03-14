import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple
import os

logger = logging.getLogger(__name__)

class CSVLoader:
    """Utility for loading and processing CSV files."""
    
    def __init__(self, file_path: str):
        """
        Initialize the CSV loader.
        
        Args:
            file_path: Path to the CSV file
        """
        self.file_path = file_path
        self.df = None
        self.metadata = {}
        logger.info(f"Initialized CSV loader for file: {file_path}")
    
    def load(self) -> bool:
        """
        Load the CSV file into a pandas DataFrame.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.file_path):
                logger.error(f"File not found: {self.file_path}")
                return False
                
            self.df = pd.read_csv(self.file_path)
            logger.info(f"Successfully loaded CSV with shape: {self.df.shape}")
            self._extract_metadata()
            return True
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            return False
    
    def _extract_metadata(self) -> None:
        """Extract and store metadata about the DataFrame."""
        if self.df is None:
            return
            
        self.metadata = {
            "num_rows": len(self.df),
            "num_columns": len(self.df.columns),
            "columns": list(self.df.columns),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "missing_values": self.df.isna().sum().to_dict(),
            "sample_rows": self.df.head(5).to_dict(orient="records")
        }
        
        # Add basic statistics for numeric columns
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if numeric_cols:
            self.metadata["numeric_stats"] = {
                col: {
                    "min": float(self.df[col].min()),
                    "max": float(self.df[col].max()),
                    "mean": float(self.df[col].mean()),
                    "median": float(self.df[col].median())
                } for col in numeric_cols
            }
    
    def get_summary(self) -> str:
        """
        Get a text summary of the CSV data.
        
        Returns:
            A string containing a summary of the data
        """
        if self.df is None:
            return "No data loaded."
            
        summary = [
            f"CSV Summary for {os.path.basename(self.file_path)}:",
            f"- Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns",
            f"- Columns: {', '.join(self.df.columns)}",
            "- Data types:",
        ]
        
        for col, dtype in self.metadata["dtypes"].items():
            summary.append(f"  - {col}: {dtype}")
        
        summary.append("- Sample data (first 5 rows):")
        for i, row in enumerate(self.metadata["sample_rows"][:5]):
            summary.append(f"  - Row {i}: {row}")
            
        if "numeric_stats" in self.metadata:
            summary.append("- Numeric column statistics:")
            for col, stats in self.metadata["numeric_stats"].items():
                summary.append(f"  - {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, mean={stats['mean']:.2f}")
        
        return "\n".join(summary)
    
    def execute_pandas_operation(self, operation: str) -> Tuple[Any, str]:
        """
        Execute a pandas operation on the DataFrame.
        
        Args:
            operation: The operation to execute (as a string)
            
        Returns:
            Tuple of (result, description)
        """
        if self.df is None:
            return None, "No data loaded."
            
        try:
            # For safety, we'll restrict the allowed operations
            # This is a simplified approach - in a real application, you'd want more robust security
            
            # Define safe operations
            safe_operations = {
                "df.head()": lambda: self.df.head(),
                "df.tail()": lambda: self.df.tail(),
                "df.describe()": lambda: self.df.describe(),
                "df.info()": lambda: self.df.info(),
                "df.isna().sum()": lambda: self.df.isna().sum(),
                "df.shape": lambda: self.df.shape,
                "df.columns": lambda: self.df.columns.tolist(),
                "df.dtypes": lambda: self.df.dtypes.to_dict()
            }
            
            # Add column-specific operations
            for col in self.df.columns:
                col_str = f"'{col}'" if not col.isalnum() else col
                
                # Add value counts for this column
                safe_operations[f"df[{col_str}].value_counts()"] = lambda c=col: self.df[c].value_counts().to_dict()
                
                # Add basic statistics for numeric columns
                if self.df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    safe_operations[f"df[{col_str}].mean()"] = lambda c=col: float(self.df[c].mean())
                    safe_operations[f"df[{col_str}].median()"] = lambda c=col: float(self.df[c].median())
                    safe_operations[f"df[{col_str}].min()"] = lambda c=col: float(self.df[c].min())
                    safe_operations[f"df[{col_str}].max()"] = lambda c=col: float(self.df[c].max())
                    safe_operations[f"df[{col_str}].sum()"] = lambda c=col: float(self.df[c].sum())
            
            # Check if operation is in safe operations
            operation = operation.strip()
            if operation in safe_operations:
                result = safe_operations[operation]()
                return result, f"Successfully executed: {operation}"
            
            # For groupby and more complex operations, we'll need custom handling
            if operation.startswith("df.groupby("):
                # Very simplistic parsing, would need to be more robust in a real app
                parts = operation.split(".")
                if len(parts) >= 3 and parts[0] == "df" and parts[1].startswith("groupby"):
                    group_col = parts[1].split("(")[1].split(")")[0].strip("'\"")
                    agg_func = parts[2].split("(")[0]
                    
                    if agg_func in ["mean", "sum", "count", "min", "max"]:
                        # Execute the groupby operation
                        grouped = getattr(self.df.groupby(group_col), agg_func)()
                        return grouped.to_dict(), f"Successfully executed groupby: {operation}"
            
            return None, f"Operation not allowed for security reasons: {operation}"
        except Exception as e:
            logger.error(f"Error executing pandas operation: {str(e)}")
            return None, f"Error: {str(e)}"