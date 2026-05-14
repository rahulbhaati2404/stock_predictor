from typing import TypedDict


class AgentState(TypedDict):
    input: str
    decision: str
    ticker: str
    output: str