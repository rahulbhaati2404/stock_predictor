import autogen
import os
from config.ai_config import config_list, llm_config
from config.logger_util import logger

logger.info(f"Stock Sentiments File Called")

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

# Agent B: The NEW Pattern Analyzer Expert
pattern_analyzer = autogen.AssistantAgent(
    name="Pattern_Analyzer_Expert",
    llm_config=llm_config,
    system_message=(
        "You are a Senior Technical Analyst. Your job is to review the data, code output, or charts "
        "provided by other agents. Look at multiple indicators simultaneously (e.g., Moving Averages, RSI, MACD). "
        "Synthesize this information to provide a clear, final trading decision. "
        "You must end your final message with either 'DECISION: BUY' or 'DECISION: HOLD/SELL'."
    )
)

# Agent C: The Code Executor
user_proxy = autogen.UserProxyAgent(
    name="Execution_Engine",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=4,  # Increased slightly to accommodate group chat steps
    code_execution_config={
        "work_dir": work_dir,
        "use_docker": False
    }
)


def verify_math(ticker):
    logger.info(f"Autogen Verify Math Called for {ticker}")
    if "." not in ticker: 
        ticker = f"{ticker}.NS"

    # Expanded task requiring multiple indicators
    task = (
        f"1. Technical_Coder: Write a python script to fetch 60 days of data for {ticker} using yfinance.\n"
        "2. Calculate a 20-day Simple Moving Average (SMA), RSI (Relative Strength Index), and MACD.\n"
        "3. Print the latest values of these indicators cleanly.\n"
        f"4. Execution_Engine: Run the script.\n"
        f"5. Pattern_Analyzer_Expert: Analyze the printed indicator values simultaneously and make a final decision.\n"
        "End your final analysis explicitly with 'DECISION: BUY' or 'DECISION: HOLD/SELL'."
    )

    # 3. Group Chat Setup (Orchestrates 3+ agents)
    groupchat = autogen.GroupChat(
        agents=[user_proxy, assistant, pattern_analyzer], 
        messages=[], 
        max_round=10
    )
    
    manager = autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=llm_config
    )

    # 4. Initiate Chat through the Manager
    chat_result = user_proxy.initiate_chat(
        manager,
        message=task,
        summary_method="last_msg"
    )

    output = chat_result.summary
    return "BUY" if "DECISION: BUY" in output.upper() else "HOLD/SELL"