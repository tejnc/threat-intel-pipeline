from typing import Any

from src.embedding.nlp import Embedder
from src.storage.graph_db import Graph
from src.queries import across_campaigns, clusters_by_handle, timeline

# Singleton-ish reuse across tool calls
_GRAPH = Graph()
_EMB = Embedder()


def tool_search(query: str, k: int = 10) -> list[dict[str, Any]]:
    """
    Hybrid RAG search over chunks in Neo4j using keyword + embeddings.
    Returns [{id, text, _score}, ...]
    """
    vec = _EMB.embed([query])[0]
    return _GRAPH.hybrid_search(query, vec, k=k)


def tool_context(indicator_value: str) -> list[dict[str, Any]]:
    """
    Context snippets (chunk text + doc id + confidence + ts) for an Indicator.
    """
    return _GRAPH.context_for_indicator(indicator_value)


def tool_relationships(indicator: str, hops: int = 1) -> list[dict[str, Any]]:
    """
    Related indicators/documents up to N hops.
    """
    return _GRAPH.relationships(indicator, hops=hops)


def tool_network(indicator: str, hops: int = 2) -> dict[str, Any]:
    """
    Small neighborhood network: {nodes: [...], links: [...]}
    """
    return _GRAPH.network(indicator, hops=hops)


def tool_clusters_by_handle() -> list[dict[str, Any]]:
    """
    Social handle co-mention clusters (edge list).
    """
    return clusters_by_handle(_GRAPH)


def tool_across_campaigns() -> list[dict[str, Any]]:
    """
    Indicators that appear across multiple campaigns.
    """
    return across_campaigns(_GRAPH)


def tool_timeline(indicator_or_handle: str) -> list[dict[str, Any]]:
    """
    Timeline (ts + evidence) for an indicator/handle.
    """
    return timeline(_GRAPH, indicator_or_handle)


def tool_indicator_lookup(typ: str) -> list[str]:
    """
    Lookup distinct indicator values by type (domain, ip, url, email, social:*, phone, ...).
    """
    return _GRAPH.indicator_lookup(typ)
