import re
from typing import TypedDict, Any 
from langgraph.graph import StateGraph, START, END

from src.agent.tools import *

class AgentState(TypedDict):
    query: str
    result: Any
    

# Regex helpers to detect indicators
RE_URL = re.compile(r"https?://\S+|www\.\S+")
RE_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RE_SOCIAL = re.compile(r"\b(?:t\.me|twitter\.com|x\.com|youtube\.com)/\S+\b", re.I)

def detect_indicator(q: str) -> str | None:
    for regex in (RE_URL, RE_IP, RE_EMAIL, RE_SOCIAL):
        m = regex.search(q)
        if m: return m.group(0)
    return None


# def router_fn(state: AgentState):
#     q = state["query"].lower()
#     ind = detect_indicator(state["query"])
#     if "cluster" in q: return {"action": "clusters"}
#     if "campaign" in q: return {"action": "across"}
#     if "timeline" in q: return {"action": "timeline", "indicator": ind or state["query"]}
#     if "network" in q: return {"action": "network", "indicator": ind}
#     if "relationship" in q: return {"action": "relationships", "indicator": ind}
#     if "context" in q: return {"action": "context", "indicator": ind}
#     if ind: return {"action": "context", "indicator": ind}
#     return {"action": "search", "query": state["query"]}

def router_fn(state: AgentState):
    q = state["query"].lower()
    print("q", q)
    return "search"
    # if "timeline" in q:
    #     return "timeline"
    # elif "across" in q and "campaign" in q:
    #     return "across_campaigns"
    # else:
    #     return "search"

def tool_search(query):
    return {"search_query", query}

workflow = StateGraph(AgentState)

# add nodes
workflow.add_node("router", router_fn)
workflow.add_node("search", tool_search)
# workflow.add_node("context", tool_context)
# workflow.add_node("indicator_lookup", tool_indicator_lookup)
# workflow.add_node("timeline", tool_timeline)
# workflow.add_node("across_campaigns", tool_across_campaigns)

# connecting edges
workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    lambda state: router_fn(state),  # routing logic
    {
        "search": "search",
        # "timeline": "timeline",
        # "context": "context",
        # "indicator_lookup": "indicator_lookup",
        # "across_campaigns": "across_campaigns",
    },
)
workflow.add_edge("search", END)
# workflow.add_edge("timeline", END)
# workflow.add_edge("context", END)
# workflow.add_edge("indicator_lookup", END)
# workflow.add_edge("across_campaigns", END)

# compile agent
agent = workflow.compile()