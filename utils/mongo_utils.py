from pymongo import MongoClient
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        """Initialize MongoDB client."""
        self.client = MongoClient(connection_string)
        self.db = None
        self.collection = None
        logger.info("Initialized MongoDB client")
    
    def set_database(self, db_name: str) -> None:
        """Set the database to use."""
        self.db = self.client[db_name]
        logger.info(f"Set database to: {db_name}")
    
    def set_collection(self, collection_name: str) -> None:
        """Set the collection to use."""
        if self.db is None:
            raise ValueError("Database not set. Call set_database first.")
        self.collection = self.db[collection_name]
        logger.info(f"Set collection to: {collection_name}")
    
    def find(self, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """Execute find query."""
        if self.collection is None:
            raise ValueError("Collection not set. Call set_collection first.")
        return list(self.collection.find(query).limit(limit))
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute find_one query."""
        if self.collection is None:
            raise ValueError("Collection not set. Call set_collection first.")
        return self.collection.find_one(query)
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a single document."""
        if self.collection is None:
            raise ValueError("Collection not set. Call set_collection first.")
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update a single document."""
        if self.collection is None:
            raise ValueError("Collection not set. Call set_collection first.")
        result = self.collection.update_one(query, {"$set": update})
        return result.modified_count
    
    def delete_one(self, query: Dict[str, Any]) -> int:
        """Delete a single document."""
        if self.collection is None:
            raise ValueError("Collection not set. Call set_collection first.")
        result = self.collection.delete_one(query)
        return result.deleted_count
    
    def count_documents(self, query: Dict[str, Any]) -> int:
        """Count documents matching query."""
        if self.collection is None:
            raise ValueError("Collection not set. Call set_collection first.")
        return self.collection.count_documents(query)
    
    def close(self) -> None:
        """Close the MongoDB connection."""
        self.client.close()
        logger.info("Closed MongoDB connection") 