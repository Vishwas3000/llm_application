data-analysis-agent/
│
├── requirements.txt           # Project dependencies
├── .env                       # Environment variables
│
├── app.py                     # Main application entry point
├── config.py                  # Configuration settings
│
├── agent/
│   ├── __init__.py
│   ├── agent.py               # Agent implementation
│   ├── memory.py              # Memory implementation
│   ├── tools.py               # Tools implementation
│   └── prompts.py             # Prompt templates
│
├── data/
│   └── sample.csv             # Sample data for testing
│
└── utils/
    ├── __init__.py
    ├── csv_loader.py          # CSV file loading utilities
    ├── llm.py                 # LLM interface with Ollama
    └── helpers.py             # Helper functions