# 📈 StocksPredictor AI
A high-performance, modular AI system for Indian Stock Market (NSE) analysis. Built with a multi-agent architecture to identify breakouts and audit portfolios using local LLMs.

## 🌟 Key Features
- **Intelligent Routing:** Uses **LangGraph** to classify user intent and route queries to specialized nodes.
- **Multi-Agent Workforce:** Powered by **CrewAI**, featuring a Technical Analyst and a Risk Manager.
- **Local & Private:** Runs entirely on your machine using **Ollama** (Llama 3.1).
- **Live Observability:** Real-time progress updates in the UI to track agent thinking stages.
- **Math Verification:** Integrated **AutoGen** for executing Python scripts to verify technical indicators.

## 📂 Project Structure
```text
stocks_predictor/
├── core/               # AI Logic (Workflow, Agents, LLM Setup)
├── tools/              # Market Scraping & NSE Data Tools
├── memory/             # Vector Database & Document Indexing
├── main.py             # Gradio UI & Entry Point
├── setup.sh            # Automated Environment Setup
└── requirements.txt    # Project Dependencies