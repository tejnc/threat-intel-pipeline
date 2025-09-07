# src/queries.py
from src.storage.graph_db import Graph


def graph_two_hop(graph: Graph, value: str):
    """Find all indicators within 2 hops of a given indicator value."""
    return graph.relationships(value, hops=2)


def clusters_by_handle(graph: Graph):
    """
    Group social:* indicators by co-mentions in documents.
    Acts as a simple community proxy for social accounts mentioned together.
    """
    q = (
        "MATCH (i:Indicator)-[:MENTIONED_IN]->(d:Document)<-[:MENTIONED_IN]-(j:Indicator)\n"
        "WHERE i.type STARTS WITH 'social:' AND j.type STARTS WITH 'social:' AND i<>j\n"
        "RETURN i.value AS a, j.value AS b, count(*) AS w ORDER BY w DESC LIMIT 100"
    )
    with graph.driver.session() as s:
        return [dict(r) for r in s.run(q)]


def across_campaigns(graph: Graph):
    """
    Find indicators that appear in more than one campaign.
    """
    q = (
        "MATCH (i:Indicator)-[:MENTIONED_IN]->(d:Document)-[:PART_OF_CAMPAIGN]->(c:Campaign)\n"
        "WITH i, collect(DISTINCT c.name) AS camps\n"
        "WHERE size(camps) > 1\n"
        "RETURN i.value AS indicator, camps"
    )
    with graph.driver.session() as s:
        return [dict(r) for r in s.run(q)]


def timeline(graph: Graph, value: str):
    """
    Build a timeline of when an indicator was mentioned (by document timestamp).
    """
    q = (
        "MATCH (i:Indicator {value:$v})-[r:MENTIONED_IN]->(d:Document)\n"
        "RETURN d.id AS documentId, r.ts AS ts ORDER BY ts"
    )
    with graph.driver.session() as s:
        return [dict(r) for r in s.run(q, v=value)]
