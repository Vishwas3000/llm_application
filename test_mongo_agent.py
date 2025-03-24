import asyncio
import json
from utils.mongo_utils import MongoDBClient
from agent.tools import create_standard_tools

async def test_mongo_queries():
    # Initialize MongoDB client
    mongo_client = MongoDBClient("mongodb://localhost:27017/")
    mongo_client.set_database("mydatabase")
    mongo_client.set_collection("users")
    
    # Create tool registry
    registry = create_standard_tools()
    registry.set_mongo_client(mongo_client)
    
    # Test 1: Insert a user
    insert_query = {
        "operation": "insert_one",
        "document": {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "city": "New York"
        }
    }
    print("\nTest 1: Inserting a user")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(insert_query))
    print(f"Result: {result}")
    print(f"Description: {description}")
    
    # Test 2: Find the inserted user
    find_query = {
        "operation": "find_one",
        "query": {"email": "john@example.com"}
    }
    print("\nTest 2: Finding the inserted user")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(find_query))
    print(f"Result: {result}")
    print(f"Description: {description}")
    
    # Test 3: Update the user
    update_query = {
        "operation": "update_one",
        "query": {"email": "john@example.com"},
        "update": {"age": 31, "city": "San Francisco"}
    }
    print("\nTest 3: Updating the user")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(update_query))
    print(f"Result: {result}")
    print(f"Description: {description}")
    
    # Test 4: Find all users over 25
    find_all_query = {
        "operation": "find",
        "query": {"age": {"$gt": 25}},
        "limit": 10
    }
    print("\nTest 4: Finding all users over 25")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(find_all_query))
    print(f"Result: {result}")
    print(f"Description: {description}")
    
    # Test 5: Count users
    count_query = {
        "operation": "count",
        "query": {"age": {"$gt": 25}}
    }
    print("\nTest 5: Counting users over 25")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(count_query))
    print(f"Result: {result}")
    print(f"Description: {description}")
    
    # Test 6: Delete the test user
    delete_query = {
        "operation": "delete_one",
        "query": {"email": "john@example.com"}
    }
    print("\nTest 6: Deleting the test user")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(delete_query))
    print(f"Result: {result}")
    print(f"Description: {description}")
    
    # Close MongoDB connection
    mongo_client.close()

if __name__ == "__main__":
    asyncio.run(test_mongo_queries()) 