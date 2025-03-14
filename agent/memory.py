from typing import List, Dict, Any, Optional
import logging
from config import MEMORY_SIZE

logger = logging.getLogger(__name__)

class AgentMemory:
    """Memory system for the agent to store information and interaction history."""
    
    def __init__(self, max_entries: int = MEMORY_SIZE):
        """
        Initialize the agent memory.
        
        Args:
            max_entries: Maximum number of memory entries to store
        """
        self.memories: List[Dict[str, Any]] = []
        self.max_entries = max_entries
        self.csv_metadata: Dict[str, Any] = {}
        logger.info(f"Initialized agent memory with max entries: {max_entries}")
    
    def add_entry(self, entry_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new memory entry.
        
        Args:
            entry_type: Type of memory entry (e.g., 'observation', 'tool_result', 'decision')
            content: The content of the memory
            metadata: Additional metadata for the memory
        """
        entry = {
            "type": entry_type,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.memories.append(entry)
        
        # Keep memory within size limit
        if len(self.memories) > self.max_entries:
            self.memories.pop(0)
            
        logger.debug(f"Added memory entry of type: {entry_type}")
    
    def set_csv_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set metadata about the loaded CSV file.
        
        Args:
            metadata: Dictionary containing metadata about the CSV
        """
        self.csv_metadata = metadata
        self.add_entry("csv_loaded", f"Loaded CSV file with {metadata.get('num_rows', 0)} rows and {metadata.get('num_columns', 0)} columns")
        logger.info(f"Set CSV metadata, {metadata.get('num_rows', 0)} rows and {metadata.get('num_columns', 0)} columns")
    
    def get_formatted_memory(self) -> str:
        """
        Get a formatted string representation of the memory.
        
        Returns:
            String representation of the memory
        """
        if not self.memories and not self.csv_metadata:
            return "<Empty>"
            
        memory_str = []
        
        # Add CSV metadata if available
        if self.csv_metadata:
            memory_str.append("CSV Data:")
            if "columns" in self.csv_metadata:
                memory_str.append(f"- Columns: {', '.join(self.csv_metadata['columns'])}")
            if "num_rows" in self.csv_metadata:
                memory_str.append(f"- Rows: {self.csv_metadata['num_rows']}")
            if "sample_rows" in self.csv_metadata and self.csv_metadata["sample_rows"]:
                memory_str.append("- Sample Data:")
                for i, row in enumerate(self.csv_metadata["sample_rows"][:3]):
                    memory_str.append(f"  Row {i+1}: {row}")
            
            # Add numeric stats if available
            if "numeric_stats" in self.csv_metadata:
                memory_str.append("- Numeric Column Statistics:")
                for col, stats in self.csv_metadata["numeric_stats"].items():
                    stats_str = ", ".join([f"{k}={v:.2f}" for k, v in stats.items()])
                    memory_str.append(f"  {col}: {stats_str}")
            
            memory_str.append("")
        
        # Add memory entries
        if self.memories:
            memory_str.append("Previous Operations:")
            for i, memory in enumerate(self.memories):
                content = memory["content"]
                # Truncate long content
                if len(content) > 100:
                    content = content[:97] + "..."
                memory_str.append(f"{i+1}. [{memory['type']}] {content}")
        
        return "\n".join(memory_str)
    
    def clear(self) -> None:
        """Clear all memory entries."""
        self.memories = []
        logger.info("Cleared agent memory")