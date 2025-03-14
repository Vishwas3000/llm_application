import json
import httpx
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class LLMInterface:
    """Interface for interacting with Ollama LLM."""
    
    def __init__(self, model_name: str = "deepseek-r1", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.api_url = f"{host}/api/generate"
        logger.info(f"Initialized LLM interface with model: {model_name}")
        
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt to send to the LLM
            temperature: Controls randomness (higher = more random)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The LLM response as a string
        """
        logger.debug(f"Sending prompt to LLM: {prompt[:100]}...")
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False  # Set to False to get a complete response
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # Increased timeout
                response = await client.post(self.api_url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    error_msg = f"Ollama API returned status code {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}"
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            return f"Error: LLM request failed with status code {e.response.status_code}"
        except httpx.ReadTimeout:
            logger.error("Request to Ollama timed out")
            return "Error: Request to Ollama timed out. The model might be still loading or the server is busy."
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return f"Error: {str(e)}"
    
    async def parse_tool_call(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract tool calls.
        
        Args:
            response: The LLM response
            
        Returns:
            A dictionary containing the tool name and input
        """
        try:
            # Look for JSON block in the response
            start_idx = response.find("```json")
            if start_idx == -1:
                start_idx = response.find("{")
            else:
                start_idx = response.find("{", start_idx)
                
            end_idx = response.rfind("}")
            
            if start_idx == -1 or end_idx == -1:
                logger.warning("Could not find JSON in response")
                return {"tool_name": "Generate_Final_Answer", "tool_input": response}
            
            json_str = response[start_idx:end_idx+1]
            
            # Clean up JSON string - sometimes LLMs generate invalid JSON
            json_str = json_str.replace('\n', ' ').strip()
            # Remove any trailing commas before closing brackets
            json_str = json_str.replace(',}', '}').replace(', }', '}')
            json_str = json_str.replace(',]', ']').replace(', ]', ']')
            
            tool_call = json.loads(json_str)
            
            # Ensure we have the expected keys
            if "tool_name" not in tool_call:
                logger.warning("No tool_name in parsed JSON")
                return {"tool_name": "Generate_Final_Answer", "tool_input": response}
                
            return tool_call
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {response[:200]}... Error: {str(e)}")
            return {"tool_name": "Generate_Final_Answer", "tool_input": response}
        except Exception as e:
            logger.error(f"Error parsing tool call: {str(e)}")
            return {"tool_name": "Generate_Final_Answer", "tool_input": response}