from fastapi import APIRouter, FastAPI, Query

from src.embedding.nlp import Embedder
from src.pipeline import run_pipeline
from src.queries import (across_campaigns, clusters_by_handle, graph_two_hop,
                         timeline)
from src.storage.graph_db import Graph

# Initialize Neo4j + Embeddings
_graph = Graph()
_graph.init_schema()
_embedder = Embedder()

# Define router
router = APIRouter()

# -- running pipeline --
@router.get("/start_pipeline")
async def pipeline():
    run_pipeline()
    return  {"Message": "Pipeline ran successfully."}

# ---------- Health ----------
@router.get("/health")
async def health():
    return {"ok": True}

# ---------- Search ----------
@router.get("/search")
async def search(q: str = Query(...), k: int = 10):
    """
    performs hybrid search: vector + keyword; rank by combined score
    example queries: What Russian disinformation campaigns target France?
    """
    vec = _embedder.embed([q])[0]
    results = _graph.hybrid_search(q, vec, k=k)
    return {
        "results": [
            {"chunkId": r.get("id"), "text": r.get("text"), "score": r.get("_score")}
            for r in results
        ]
    }

# ---------- Indicators ----------
@router.get("/indicators/{typ}")
async def indicators(typ: str):
    """
        Lookup indicators by type.

        Args:
            typ: e.g. 'domain', 'ip', 'phone'
    """
    return {"results": _graph.indicator_lookup(typ)}


@router.get("/context/{indicator}")
async def context(indicator: str):
    """
        Retrieve document and chunk context where an indicator was mentioned.

        Args:
            value: indicator value
    """
    return {"context": _graph.context_for_indicator(indicator)}


# ---------- Relationships & Network ----------
@router.get("/relationships/{indicator}")
async def rels(indicator: str, hops: int = 1):
    """
        Explore related indicators up to N hops.

        Args:
            value: indicator value
            hops: traversal depth
    """
    return {"related": _graph.relationships(indicator, hops=hops)}


@router.get("/network/{indicator}")
async def network(indicator: str, hops: int = 2):
    """
        Return network graph of indicators around a given indicator.

        Args:
            value: indicator value
            hops: traversal depth (default: 2)
        Returns:
            dict with 'nodes' and 'links' suitable for visualization
    """
    return _graph.network(indicator, hops=hops)


# ---------- Assignment Test Queries ----------
@router.get("/test/semantic")
async def q_semantic():
    q = "What Russian disinformation campaigns target France?"
    vec = _embedder.embed([q])[0]
    return {"results": _graph.hybrid_search(q, vec, k=10)}

@router.get("/test/lookup/doppelgaenger")
async def q_lookup():
    return {"domains": _graph.indicator_lookup("domain")}

@router.get("/test/twohop")
async def q_twohop(value: str):
    return {"twoHop": graph_two_hop(_graph, value)}

@router.get("/test/clusters")
async def q_clusters():
    return {"clusters": clusters_by_handle(_graph)}

@router.get("/test/across-campaigns")
async def q_across():
    return {"indicators": across_campaigns(_graph)}

@router.get("/test/timeline")
async def q_timeline(value: str):
    return {"timeline": timeline(_graph, value)}

# langgraph agent
from src.agent.langgraph_agent import agent

@router.get("/agent")
async def agent_query(q: str):
    state = {"query": q}
    res = agent.invoke(state)
    return {"query": q, "answer": res.get("result")}


# Main FastAPI app
app = FastAPI(title="Threat Intel Pipeline RAG ")
app.include_router(router)
