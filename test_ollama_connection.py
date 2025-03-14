#!/usr/bin/env python3
"""
Direct test of Ollama connection using httpx.
"""
import asyncio
import httpx
import json
import time

async def test_ollama_connection():
    """
    Test the direct connection to Ollama.
    """
    print("Testing direct connection to Ollama...")
    
    try:
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": "deepseek-r1",
            "prompt": "Hello, are you working? Please respond with a short message.",
            "stream": False
        }
        
        start_time = time.time()
        print("Sending request to Ollama...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            elapsed = time.time() - start_time
            print(f"Received response in {elapsed:.2f} seconds.")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Ollama connection successful!")
                print(f"Model: {payload['model']}")
                print(f"Response: {result.get('response', '')}")
            else:
                print(f"\n❌ Error: Ollama returned status code {response.status_code}")
                print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Error connecting to Ollama: {str(e)}")
        print("\nPlease check:")
        print("1. Is Ollama running? Run 'ollama serve' in another terminal.")
        print("2. Is the model installed? Run 'ollama pull deepseek-r1'.")
        print("3. Is the URL correct? Default is http://localhost:11434.")

if __name__ == "__main__":
    asyncio.run(test_ollama_connection())