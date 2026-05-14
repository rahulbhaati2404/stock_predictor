from crewai import Agent
from services.ollama_service import get_llm_with_reconnect
from tools.web_tools import search_web_for_stocks

llm_brain = get_llm_with_reconnect()

manager = Agent(
    role='Portfolio Risk Manager',
    goal='Audit user holdings.',
    backstory='Cold calculated risk manager.',
    tools=[search_web_for_stocks],
    llm=llm_brain,
    verbose=True,
    allow_delegation=False
)