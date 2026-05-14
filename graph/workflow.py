from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.router import router_node
from graph.nodes import (
    search_web_node,
    analysis_node,
    portfolio_manager_node,
    off_topic_node
)



def build_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("search_web_node", search_web_node)
    workflow.add_node("analysis_node", analysis_node)
    workflow.add_node("portfolio_manager_node", portfolio_manager_node)
    workflow.add_node("off_topic_node", off_topic_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        lambda x: x["decision"],
        {
            "SEARCH_WEB": "search_web_node",
            "ANALYSIS": "analysis_node",
            "MANAGER": "portfolio_manager_node",
            "OFF_TOPIC": "off_topic_node"
        }
    )

    workflow.add_edge("search_web_node", END)
    workflow.add_edge("analysis_node", END)
    workflow.add_edge("portfolio_manager_node", END)
    workflow.add_edge("off_topic_node", END)

    return workflow.compile()