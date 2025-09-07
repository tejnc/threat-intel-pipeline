import re
from typing_extensions import TypedDict
from typing import Any

from langgraph.graph import StateGraph, START

from src.agent.tools import *
from src.extraction.indicators import extract_indicators

class AgentState(TypedDict):
    query: str
    result: Any
    
# Regex helpers to detect indicators
RE_URL = re.compile(r"https?://\S+|www\.\S+")
RE_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RE_SOCIAL = re.compile(r"\b(?:t\.me|twitter\.com|x\.com|youtube\.com)/\S+\b", re.I)

def detect_indicator(q: str) -> bool:
    return any(regex.search(q) for regex in (RE_URL, RE_IP, RE_EMAIL, RE_SOCIAL))

def router_fn(state: AgentState):
    q = state["query"].lower()
    ind_present = detect_indicator(state["query"])
    if "cluster" in q: 
        print("cluster search")
        res = tool_clusters_by_handle()
        return {"action": "clusters", "query": state["query"], "result": res}
    # elif "campaign" in q: 
    #     print("campaign router")
    #     res = tool_across_campaigns()
    #     return {"action": "across", "query": state["query"], "result": res}
    elif "timeline" in q:
        print("timeline router")
        value = q.replace("timeline", "").strip()
        res = tool_timeline(value) 
        return {"action": "timeline", "query":state["query"], "result": res}
    elif "network" in q: 
        value = q.replace("network", "").strip()
        res = tool_network(value) 
        return {"action": "network", "indicator": q, "result": res}
    # elif "relationship" in q: 
    #     return {"action": "relationships", "indicator": q}
    elif ind_present or "context" in q: 
        print("indicator look route")
        # grab only the indicator
        # values:list = extract_indicators(q)
        if "context" in q:
            q = q.replace("context", "").strip()
        res = tool_context(indicator_value=q)
        return {"action": "context", "query": state["query"], "result": res}
    else:
        res= tool_search(query=q, k=2)
        # return {"action": "search", "query": state["query"], "result": [{"chunks":r["text"]} for r in res]}
        return {"action": "search", "query": state["query"], "result": res[0]["text"]}

# start the workflow
workflow = StateGraph(AgentState)

#add nodes
workflow.add_node("router", router_fn)

# add edges
workflow.add_edge(START, "router")

# compile
agent = workflow.compile()

# invoke
# res = agent.invoke({"query":"t.me"})
# print("response",  res)