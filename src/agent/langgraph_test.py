from typing_extensions import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph

class State(TypedDict):
    x: int

def my_node(state: State, config: RunnableConfig) -> State:
    return {"x": state["x"] + 1}

builder = StateGraph(State)
builder.add_node(my_node)  # node name will be 'my_node'
builder.add_edge(START, "my_node")
graph = builder.compile()
res = graph.invoke({"x": 1})
print(res)
# {'x': 2}