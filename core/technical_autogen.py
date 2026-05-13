import autogen
import os

# Config for local AutoGen
config_list = [
    {
        "model": "llama3.1",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
]

def verify_math(ticker):
    """Uses AutoGen to write and execute a script to verify stock math."""
    if "." not in ticker: ticker = f"{ticker}.NS"

    assistant = autogen.AssistantAgent(
        name="Technical_Coder",
        llm_config={"config_list": config_list, "temperature": 0.1},
        system_message="Provide only python code blocks using yfinance."
    )

    user_proxy = autogen.UserProxyAgent(
        name="Execution_Engine",
        human_input_mode="NEVER",
        code_execution_config={"work_dir": "coding", "use_docker": False}
    )

    task = (f"Fetch 30d data for {ticker}. Calculate 20d MA. "
            f"Is Price > 10% above MA? Print 'RESULT: YES' or 'NO'.")

    chat_result = user_proxy.initiate_chat(assistant, message=task, summary_method="last_msg")
    return "YES" if "YES" in chat_result.summary.upper() else "NO"