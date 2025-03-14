import asyncio
import logging
import os
import typer
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from config import OLLAMA_HOST, OLLAMA_MODEL, LOG_LEVEL
from utils.helpers import setup_logging
from utils.llm import LLMInterface
from agent.agent import DataAnalysisAgent
from agent.memory import AgentMemory
from agent.tools import create_standard_tools

# Set up logging
setup_logging(LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create console for rich output
console = Console()

app = typer.Typer()

async def run_agent(file_path: str, question: str = None, use_streaming: bool = True):
    """
    Run the data analysis agent on a CSV file.
    
    Args:
        file_path: Path to the CSV file
        question: Optional initial question to ask
        use_streaming: Whether to use streaming output
    """
    try:
        # Initialize components
        llm = LLMInterface(model_name=OLLAMA_MODEL, host=OLLAMA_HOST)
        memory = AgentMemory()
        tools = create_standard_tools()
        
        # Create agent
        agent = DataAnalysisAgent(llm, tools, memory)
        
        # Load CSV file
        console.print(f"[bold blue]Loading CSV file:[/] {file_path}")
        success = agent.load_csv(file_path)
        
        if not success:
            console.print("[bold red]Failed to load CSV file.[/]")
            return
        
        console.print("[bold green]CSV file loaded successfully![/]")
        
        # Interactive loop
        while True:
            if question:
                user_question = question
                question = None  # Only use the provided question once
            else:
                user_question = Prompt.ask("\n[bold cyan]Enter your question[/] (or 'exit' to quit)")
                
            if user_question.lower() in ('exit', 'quit', 'q'):
                break
            
            # Process question
            if use_streaming:
                # Define callback for streaming output
                def stream_callback(chunk: str):
                    console.print(chunk, end="")
                
                console.print("\n[bold green]Answer:[/]")
                await agent.process_question_streaming(user_question, stream_callback)
                console.print("\n")  # Add newline after response
            else:
                with console.status("[bold yellow]Thinking...[/]", spinner="dots"):
                    response = await agent.process_question(user_question)
                
                # Display response
                console.print(Panel(response, title="[bold green]Answer[/]", border_style="green"))
            
    except Exception as e:
        logger.exception("Error running agent")
        console.print(f"[bold red]Error:[/] {str(e)}")

@app.command()
def analyze(
    csv_file: str = typer.Argument(..., help="Path to the CSV file to analyze"),
    question: str = typer.Option(None, "--question", "-q", help="Initial question to ask"),
    streaming: bool = typer.Option(True, "--streaming/--no-streaming", help="Use streaming output")
):
    """
    Analyze a CSV file using the data analysis agent.
    """
    if not os.path.exists(csv_file):
        console.print(f"[bold red]Error:[/] CSV file not found: {csv_file}")
        return
    
    console.print(Panel.fit(
        "Data Analysis Agent with Ollama LLM",
        title="[bold]Welcome[/]",
        subtitle=f"Using model: [italic]{OLLAMA_MODEL}[/]",
        border_style="blue"
    ))
    
    asyncio.run(run_agent(csv_file, question, streaming))

@app.command()
def check_ollama():
    """
    Check if Ollama is running and the model is available.
    """
    async def _check():
        llm = LLMInterface(model_name=OLLAMA_MODEL, host=OLLAMA_HOST)
        with console.status("[bold yellow]Checking Ollama...[/]", spinner="dots"):
            try:
                response = await llm.generate("Hello, are you working?")
                console.print(f"[bold green]Ollama is working![/] Response: {response}")
            except Exception as e:
                console.print(f"[bold red]Error connecting to Ollama:[/] {str(e)}")
                console.print(f"Make sure Ollama is running at {OLLAMA_HOST} and the model '{OLLAMA_MODEL}' is installed.")
                console.print("You can install the model with: [bold]ollama pull deepseek-r1[/]")
    
    asyncio.run(_check())

@app.command()
def test_streaming():
    """
    Test streaming output with Ollama.
    """
    async def _test_streaming():
        console.print("[bold blue]Testing streaming output with Ollama...[/]")
        
        llm = LLMInterface(model_name=OLLAMA_MODEL, host=OLLAMA_HOST)
        
        def callback(chunk: str):
            console.print(chunk, end="")
        
        prompt = "Write a short paragraph about data analysis. Make it informative but concise."
        
        try:
            console.print("[bold green]Response:[/]\n")
            await llm.generate_streaming(prompt, callback)
            console.print("\n\n[bold green]Streaming test completed![/]")
        except Exception as e:
            console.print(f"\n[bold red]Error during streaming test:[/] {str(e)}")
    
    asyncio.run(_test_streaming())

if __name__ == "__main__":
    app()