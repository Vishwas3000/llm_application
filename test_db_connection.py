import asyncio
from utils.mongo_utils import MongoDBClient
from agent.tools import create_standard_tools
import json

async def test_connection():
    print("Testing MongoDB Connection and Tool Functionality...")
    
    try:
        # Initialize MongoDB client
        print("\n1. Initializing MongoDB client...")
        mongo_client = MongoDBClient("mongodb://localhost:27017/")
        
        # Test database connection
        print("\n2. Testing database connection...")
        mongo_client.set_database("mydatabase")
        mongo_client.set_collection("users")
        
        # Create tool registry
        print("\n3. Creating tool registry...")
        registry = create_standard_tools()
        registry.set_mongo_client(mongo_client)
        
        # Test simple insert
        print("\n4. Testing insert operation...")
        test_doc = {
            "operation": "insert_one",
            "document": {
                "name": "Test User",
                "age": 25,
                "email": "test@example.com",
                "city": "Test City"
            }
        }
        result, description = await registry.execute_tool("MongoDB_Query", json.dumps(test_doc))
        print(f"Insert Result: {result}")
        print(f"Description: {description}")
        
        # Test find operation
        print("\n5. Testing find operation...")
        find_query = {
            "operation": "find_one",
            "query": {"email": "test@example.com"}
        }
        result, description = await registry.execute_tool("MongoDB_Query", json.dumps(find_query))
        print(f"Find Result: {result}")
        print(f"Description: {description}")
        
        # Test count operation
        print("\n6. Testing count operation...")
        count_query = {
            "operation": "count",
            "query": {}
        }
        result, description = await registry.execute_tool("MongoDB_Query", json.dumps(count_query))
        print(f"Count Result: {result}")
        print(f"Description: {description}")
        
        # Clean up test data
        print("\n7. Cleaning up test data...")
        delete_query = {
            "operation": "delete_one",
            "query": {"email": "test@example.com"}
        }
        result, description = await registry.execute_tool("MongoDB_Query", json.dumps(delete_query))
        print(f"Delete Result: {result}")
        print(f"Description: {description}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
    finally:
        # Close MongoDB connection
        if 'mongo_client' in locals():
            mongo_client.close()
            print("\nMongoDB connection closed.")

if __name__ == "__main__":
    asyncio.run(test_connection()) 