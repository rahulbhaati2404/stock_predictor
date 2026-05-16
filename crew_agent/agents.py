from crewai import Agent, Task, Crew, Process, LLM
import os
from config.logger_util import logger
from config.ai_config import local_llm as llm
from tools.stock_tool import analyze_breakout_potential, audit_stock_performance, scrape_breakout_scanner, search_web_for_stocks


analyst = Agent(
    role='Technical Stock Analyst',
    goal='Extract exactly the requested number of stocks using provided tools and analyze them.',
    backstory=(
        "You are a precision-oriented NSE analyst. Your primary job is to follow instructions exactly. "
        "1. If asked for a specific number of stocks, you MUST use 'scrape_breakout_scanner' and pass that exact number to the tool. "
        "2. If asked to analyze specific tickers, use 'analyze_breakout_potential' for each. "
        "3. You never suggest stocks from your memory; you ONLY use data returned by your tools."
    ),
    # Ensure tool names here match the function names exactly
    tools=[analyze_breakout_potential, search_web_for_stocks, scrape_breakout_scanner],
    llm=llm,
    verbose=True, # Critical to see WHY the agent chooses a tool
    allow_delegation=False,
    memory=False,
    max_iter=2,            
    max_execution_time=30,
    max_rpm=10,
)

manager = Agent(
    role='Portfolio Risk Manager',
    goal='Audit user holdings by comparing live market data against risk-reward ratios.',
    backstory=(
        "You are a cold, calculated risk manager. When a user provides a list of stocks, "
        "you use 'audit_stock_performance' to get the facts. You ignore your personal opinions "
        "and only provide 'Keep' or 'Sell' based on the tool's data. You are famous for being "
        "concise and never talking more than necessary."
    ),
    tools=[audit_stock_performance, search_web_for_stocks],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=2,            
    max_execution_time=30,
    max_rpm=10,
)

logger.info("✅ Agents and LLM Re-Configured for strict instruction following.")