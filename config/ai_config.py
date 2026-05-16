from crewai import LLM
from langchain_ollama import ChatOllama

# Initialize the Ollama instance for llama3.2:1b
llm = ChatOllama(
    model="mistral",
    temperature=0,
)

local_llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434"
)

config_list = [
    {
        "model": "mistral",           # Must exactly match what you pulled in Ollama
        "base_url": "http://localhost:11434/v1", # Ollama's OpenAI-compatible endpoint
        "api_key": "ollama"               # AutoGen requires a dummy string here so it doesn't complain
    }
]

llm_config = {
    "config_list": config_list,
    "cache_seed": None,
    "temperature": 0.1
}

if __name__ == "__main__":
    # Test the LLM using the correct .invoke() method
    response = llm.invoke("What is the current stock price of TCS?")
    
    # response is an AIMessage object, .content extracts just the text string
    print(response.content)