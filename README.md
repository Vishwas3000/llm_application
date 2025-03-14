# Data Analysis Agent Project Structure

```
📂 data-analysis-agent/
│  
├── 📄 requirements.txt           # Project dependencies
├── 📄 .env                       # Environment variables
│  
├── 📄 app.py                     # Main application entry point
├── 📄 config.py                  # Configuration settings
│  
├── 📂 agent/                     # Agent-related code
│   ├── 📄 __init__.py
│   ├── 📄 agent.py               # Agent implementation
│   ├── 📄 memory.py              # Memory implementation
│   ├── 📄 tools.py               # Tools implementation
│   └── 📄 prompts.py             # Prompt templates
│  
├── 📂 data/                      # Data-related files
│   └── 📄 sample.csv             # Sample data for testing
│  
└── 📂 utils/                     # Utility functions
    ├── 📄 __init__.py
    ├── 📄 csv_loader.py          # CSV file loading utilities
    ├── 📄 llm.py                 # LLM interface with Ollama
    └── 📄 helpers.py             # Helper functions
```

## How to Install

1. **Install Ollama**
   ```sh
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Download DeepSeek-R1 from the website**
   ```sh
   ollama pull deepseek-r1
   ```

3. **Check the downloaded LLMs**
   ```sh
   ollama list
   ```

4. **Start the LLM server**
   ```sh
   ollama serve
   ```
