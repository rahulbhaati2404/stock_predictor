import re
import logging
from langchain_community.llms import Ollama
from graph.state import AgentState

logger = logging.getLogger("Router")

llm = Ollama(model="llama3.1")


def router_node(state: AgentState):
    logger.info("📩 Analyzing user intent")

    user_msg = state["input"]

    classification_prompt = f"""
    Classify the user request.

    SEARCH_WEB | number
    ANALYSIS | tickers
    MANAGER | tickers
    NONE

    User: {user_msg}
    """

    try:
        response = llm.invoke(classification_prompt).strip()

        upper_res = response.upper()

        if "SEARCH_WEB" in upper_res:
            decision = "SEARCH_WEB"
            nums = re.findall(r'\d+', response)
            count = nums[0] if nums else "3"
            final_data = f"COUNT_{count}"

        elif "ANALYSIS" in upper_res:
            decision = "ANALYSIS"
            final_data = response.split("|")[-1].strip()

        elif "MANAGER" in upper_res:
            decision = "MANAGER"
            final_data = response.split("|")[-1].strip()

        else:
            decision = "OFF_TOPIC"
            final_data = "NONE"

        return {
            "decision": decision,
            "ticker": final_data
        }

    except Exception:
        return {
            "decision": "SEARCH_WEB",
            "ticker": "COUNT_3"
        }