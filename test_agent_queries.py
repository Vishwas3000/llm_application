import asyncio
import json
from utils.mongo_utils import MongoDBClient
from agent.tools import create_standard_tools

async def simulate_agent_query(registry, query_text: str):
    """Simulate an agent processing a natural language query."""
    print(f"\nUser Query: {query_text}")
    print("Agent: Processing your request...")
    
    # Simulate agent's thinking process
    if "find all" in query_text.lower() or "show all" in query_text.lower():
        # Convert to find operation
        mongo_query = {
            "operation": "find",
            "query": {},
            "limit": 10
        }
        
        # Add filters based on query text
        if "age" in query_text and "over" in query_text:
            try:
                age = int(''.join(filter(str.isdigit, query_text)))
                mongo_query["query"]["age"] = {"$gt": age}
            except ValueError:
                print("Agent: Could not determine age from query")
                
        if "city" in query_text.lower():
            city = query_text.split("city")[1].split()[0].strip("'\".,")
            mongo_query["query"]["city"] = city
            
    elif "count" in query_text.lower():
        # Convert to count operation
        mongo_query = {
            "operation": "count",
            "query": {}
        }
        
        if "age" in query_text and "over" in query_text:
            try:
                age = int(''.join(filter(str.isdigit, query_text)))
                mongo_query["query"]["age"] = {"$gt": age}
            except ValueError:
                print("Agent: Could not determine age from query")
                
    elif "add" in query_text.lower() or "insert" in query_text.lower():
        # Example of parsing a simple insert command
        # Format expected: "add user name=John age=30 city=NewYork email=john@example.com"
        parts = query_text.split()
        document = {}
        for part in parts:
            if "=" in part:
                key, value = part.split("=")
                # Try to convert to number if possible
                try:
                    value = int(value)
                except ValueError:
                    pass
                document[key] = value
                
        mongo_query = {
            "operation": "insert_one",
            "document": document
        }
        
    elif "update" in query_text.lower():
        # Example: "update user where email=john@example.com set age=35 city=Miami"
        mongo_query = {
            "operation": "update_one",
            "query": {},
            "update": {}
        }
        
        # Parse where clause
        if "where" in query_text:
            where_part = query_text.split("where")[1].split("set")[0].strip()
            key, value = where_part.split("=")
            mongo_query["query"][key.strip()] = value.strip()
            
        # Parse set clause
        if "set" in query_text:
            set_part = query_text.split("set")[1].strip()
            updates = {}
            for update in set_part.split():
                if "=" in update:
                    key, value = update.split("=")
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    updates[key.strip()] = value
            mongo_query["update"] = updates
            
    else:
        print("Agent: I'm not sure how to process this query. Please try a different format.")
        return

    print(f"Agent: I'll execute this MongoDB query: {json.dumps(mongo_query, indent=2)}")
    result, description = await registry.execute_tool("MongoDB_Query", json.dumps(mongo_query))
    print(f"Result: {json.dumps(result, indent=2)}")
    return result

async def test_agent():
    # Initialize MongoDB client
    mongo_client = MongoDBClient("mongodb://localhost:27017/")
    mongo_client.set_database("mydatabase")
    mongo_client.set_collection("users")
    
    # Create tool registry
    registry = create_standard_tools()
    registry.set_mongo_client(mongo_client)
    
    # Test queries
    test_queries = [
        # Insert queries
        "add user name=John age=30 city=NewYork email=john@example.com",
        "add user name=Alice age=25 city=SanFrancisco email=alice@example.com",
        "add user name=Bob age=35 city=Chicago email=bob@example.com",
        
        # Find queries
        "find all users over age 25",
        "find all users in city NewYork",
        
        # Count queries
        "count users over age 30",
        
        # Update queries
        "update user where email=john@example.com set age=31 city=Miami",
        
        # Complex queries
        "find all users over age 25 in city SanFrancisco"
    ]
    
    for query in test_queries:
        await simulate_agent_query(registry, query)
        print("\n" + "="*50)
    
    # Close MongoDB connection
    mongo_client.close()

if __name__ == "__main__":
    asyncio.run(test_agent()) 