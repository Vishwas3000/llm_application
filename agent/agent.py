import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
import json

from utils.llm import LLMInterface
from agent.memory import AgentMemory
from agent.tools import ToolRegistry
from agent.prompts import PromptTemplates
from utils.csv_loader import CSVLoader
from utils.helpers import format_response_for_display

logger = logging.getLogger(__name__)

class DataAnalysisAgent:
    """Agent for data analysis using LLM and tools."""
    
    def __init__(self, llm: LLMInterface, tools: ToolRegistry, memory: AgentMemory):
        """
        Initialize the data analysis agent.
        
        Args:
            llm: The LLM interface for generating responses
            tools: Registry of tools available to the agent
            memory: Agent memory for tracking context
        """
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.prompt_templates = PromptTemplates()
        logger.info("Initialized data analysis agent")
    
    def load_csv(self, file_path: str) -> bool:
        """
        Load a CSV file for analysis.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            loader = CSVLoader(file_path)
            success = loader.load()
            
            if success:
                # Set the CSV loader in the tool registry
                self.tools.set_csv_loader(loader)
                
                # Set CSV metadata in memory
                self.memory.set_csv_metadata(loader.metadata)
                
                logger.info(f"Successfully loaded CSV file: {file_path}")
                return True
            else:
                logger.error(f"Failed to load CSV file: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            return False
    
    async def process_question(self, question: str) -> str:
        """
        Process a user question and return a response.
        
        Args:
            question: The user's question
            
        Returns:
            The agent's response
        """
        logger.info(f"Processing question: {question}")
        
        # Format system prompt with memory
        system_prompt = self.prompt_templates.get_system_prompt(
            self.memory.get_formatted_memory()
        )
        
        # Format user question
        user_prompt = self.prompt_templates.format_user_question(question)
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n{user_prompt}"
        
        # Generate initial response from LLM
        response = await self.llm.generate(full_prompt)
        
        # Parse tool call
        tool_call = await self.llm.parse_tool_call(response)
        
        # Add the agent's decision to memory
        self.memory.add_entry(
            "agent_decision", 
            f"Decided to use tool: {tool_call.get('tool_name', 'Unknown')}",
            {"tool_name": tool_call.get("tool_name"), "tool_input": tool_call.get("tool_input")}
        )
        
        # Execute the tool if one was called
        if "tool_name" in tool_call and tool_call["tool_name"] != "Generate_Final_Answer":
            # Execute tool
            tool_result, tool_description = await self.tools.execute_tool(
                tool_call["tool_name"], 
                tool_call.get("tool_input", "")
            )
            
            # Format tool response
            tool_response = self.prompt_templates.format_tool_response(
                tool_call["tool_name"], 
                tool_result
            )
            
            # Add tool result to memory
            self.memory.add_entry(
                "tool_result",
                f"Used {tool_call['tool_name']} with result: {format_response_for_display(tool_result)[:100]}...",
                {"tool_name": tool_call["tool_name"], "result": tool_result}
            )
            
            # Generate final response with tool result
            full_prompt = f"{system_prompt}\n{user_prompt}\n\nAssistant: {response}\n\n{tool_response}\n\nAssistant:"
            final_response = await self.llm.generate(full_prompt)
            
            # Check if we need another tool call
            second_tool_call = await self.llm.parse_tool_call(final_response)
            
            if "tool_name" in second_tool_call and second_tool_call["tool_name"] != "Generate_Final_Answer":
                # Execute second tool
                second_tool_result, second_tool_description = await self.tools.execute_tool(
                    second_tool_call["tool_name"], 
                    second_tool_call.get("tool_input", "")
                )
                
                # Format second tool response
                second_tool_response = self.prompt_templates.format_tool_response(
                    second_tool_call["tool_name"], 
                    second_tool_result
                )
                
                # Add second tool result to memory
                self.memory.add_entry(
                    "tool_result",
                    f"Used {second_tool_call['tool_name']} with result: {format_response_for_display(second_tool_result)[:100]}...",
                    {"tool_name": second_tool_call["tool_name"], "result": second_tool_result}
                )
                
                # Generate final response with both tool results
                full_prompt = f"{full_prompt}\n{final_response}\n\n{second_tool_response}\n\nAssistant:"
                final_response = await self.llm.generate(full_prompt)
            
            # Extract final answer
            final_tool_call = await self.llm.parse_tool_call(final_response)
            
            if final_tool_call.get("tool_name") == "Generate_Final_Answer":
                final_answer = final_tool_call.get("tool_input", final_response)
            else:
                final_answer = final_response
                
            self.memory.add_entry("final_answer", f"Provided answer: {final_answer[:100]}...")
            return final_answer
        else:
            # If the first response was a final answer
            final_answer = tool_call.get("tool_input", response)
            self.memory.add_entry("final_answer", f"Provided answer: {final_answer[:100]}...")
            return final_answer
    
    async def process_question_streaming(self, question: str, callback: Callable[[str], None]) -> str:
        """
        Process a user question and stream the response.
        
        Args:
            question: The user's question
            callback: Function to call with each chunk of the response
            
        Returns:
            The agent's complete response
        """
        logger.info(f"Processing question (streaming): {question}")
        
        # Setup is the same as the non-streaming version
        system_prompt = self.prompt_templates.get_system_prompt(
            self.memory.get_formatted_memory()
        )
        user_prompt = self.prompt_templates.format_user_question(question)
        full_prompt = f"{system_prompt}\n{user_prompt}"
        
        # For the initial tool selection, we don't stream
        # This is because we need the complete response to parse the tool call
        callback("Thinking...\n")
        response = await self.llm.generate(full_prompt)
        
        # Parse tool call
        tool_call = await self.llm.parse_tool_call(response)
        
        # Add the agent's decision to memory
        tool_name = tool_call.get("tool_name", "Unknown")
        self.memory.add_entry(
            "agent_decision", 
            f"Decided to use tool: {tool_name}",
            {"tool_name": tool_name, "tool_input": tool_call.get("tool_input")}
        )
        
        callback(f"Using {tool_name}...\n")
        
        # Execute the tool if one was called
        if "tool_name" in tool_call and tool_call["tool_name"] != "Generate_Final_Answer":
            # Execute tool
            tool_result, tool_description = await self.tools.execute_tool(
                tool_call["tool_name"], 
                tool_call.get("tool_input", "")
            )
            
            # Format tool response
            tool_response = self.prompt_templates.format_tool_response(
                tool_call["tool_name"], 
                tool_result
            )
            
            # Add tool result to memory
            self.memory.add_entry(
                "tool_result",
                f"Used {tool_call['tool_name']} with result: {format_response_for_display(tool_result)[:100]}...",
                {"tool_name": tool_call["tool_name"], "result": tool_result}
            )
            
            # Generate final response with tool result - this part we stream
            callback("\nGenerating answer based on analysis...\n\n")
            full_prompt = f"{system_prompt}\n{user_prompt}\n\nAssistant: {response}\n\n{tool_response}\n\nAssistant:"
            final_response = await self.llm.generate_streaming(full_prompt, callback)
            
            # We'll keep this simple and not do multiple tool calls in the streaming version
            # Extract final answer
            final_tool_call = await self.llm.parse_tool_call(final_response)
            
            if final_tool_call.get("tool_name") == "Generate_Final_Answer":
                final_answer = final_tool_call.get("tool_input", final_response)
            else:
                final_answer = final_response
                
            self.memory.add_entry("final_answer", f"Provided answer: {final_answer[:100]}...")
            return final_answer
        else:
            # If the first response was a final answer, stream it directly
            callback("\nGenerating answer...\n\n")
            final_answer = tool_call.get("tool_input", response)
            
            # Stream the final answer
            for char in final_answer:
                callback(char)
                await asyncio.sleep(0.01)  # Simulate streaming
                
            self.memory.add_entry("final_answer", f"Provided answer: {final_answer[:100]}...")
            return final_answer
    
    def clear_memory(self) -> None:
        """Clear the agent's memory."""
        self.memory.clear()
        logger.info("Cleared agent memory")