import autogen
import os
from config.logger_util import logger
import os
from autogen import ConversableAgent, register_function
from tools.stock_tool import scrape_breakout_scanner

logger.info(f"Stock Sentiments File Called")

llm_config = {
    "config_list": [
        {
            "model": "mistral",                  # Model pulled via Ollama
            "base_url": "http://localhost:11434/v1", # Local server port
            "api_key": "ollama",                 # Dummy key required by the API
        }
    ],
    "cache_seed": None, # Disable caching to get real-time market data
}

work_dir = "stock_analysis"

# Agent A: The Code Writer
assistant = autogen.AssistantAgent(
    name="Technical_Coder",
    llm_config=llm_config,
    system_message=(
        "You are a Python coding expert. Your ONLY job is to write complete, working Python code blocks. "
        "Use yfinance to fetch data and the 'ta' library for technical indicators. "
        "Do not write explanations, only code."
    )
)

stock_assistant = ConversableAgent(
    name="Stock_Assistant",
    system_message=(
        "You are a precise stock market tool operator. "
        "Your only job is to look at the user request and call the appropriate tool. "
        "Once a tool returns data, summarize the stock list cleanly and say TERMINATE."
    ),
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# 3. Create the User Proxy (The Executor)
# This agent doesn't think—it simply executes the python functions the assistant requests
user_proxy = ConversableAgent(
    name="User_Proxy",
    llm_config=False, # No LLM needed for the executor proxy
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    max_consecutive_auto_reply=2, # Hard limit to stop infinite loops completely!
)