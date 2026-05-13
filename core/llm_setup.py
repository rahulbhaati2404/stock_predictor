import os
import requests
import time
import logging
from crewai import LLM
from langchain_ollama import OllamaLLM

logger = logging.getLogger("LLM_Setup")

def verify_ollama_connection(base_url="http://localhost:11434"):
    """Ensures the local Ollama server is running before starting."""
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Ollama connection verified.")
                return True
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Ollama not ready. Retrying... ({i+1}/{max_retries})")
            time.sleep(3)
    
    raise ConnectionError("❌ Could not connect to Ollama. Run 'ollama serve' in your terminal.")

def get_crewai_llm(model_name="ollama/llama3.1", temperature=0.1):
    """Returns the LLM configured for CrewAI agents."""
    verify_ollama_connection()
    return LLM(
        model=model_name,
        base_url="http://localhost:11434",
        temperature=temperature,
        timeout=300
    )

def get_langchain_llm(model_name="llama3.1", temperature=0.1):
    """Returns the LLM configured for LangGraph routing."""
    verify_ollama_connection()
    return OllamaLLM(
        model=model_name,
        temperature=temperature
    )