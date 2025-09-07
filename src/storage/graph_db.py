from typing import Any

from neo4j import GraphDatabase

from src.config import settings

EMBED_DIM = 384  # all-MiniLM-L6-v2

SCHEMA_QUERIES = [
    # Constraints
    "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT ind_id IF NOT EXISTS FOR (i:Indicator) REQUIRE i.value IS UNIQUE",
    "CREATE CONSTRAINT camp_id IF NOT EXISTS FOR (c:Campaign) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT actor_id IF NOT EXISTS FOR (a:ThreatActor) REQUIRE a.name IS UNIQUE",

    # Vector indexes (native)
    f"CREATE VECTOR INDEX chunk_vec IF NOT EXISTS "
    f"FOR (c:Chunk) ON (c.embedding) "
    f"OPTIONS {{indexConfig: {{`vector.dimensions`: {EMBED_DIM}, "
    f"`vector.similarity_function`: 'cosine'}}}}",
]


class Graph:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def init_schema(self):
        with self.driver.session() as s:
            for q in SCHEMA_QUERIES:
                s.run(q)

    # ---------- Document ----------
    def upsert_document(self, doc: dict[str, Any]):
        q = "MERGE (d:Document {id:$id}) SET d += $props RETURN d"
        with self.driver.session() as s:
            s.run(q, id=doc["id"], props=doc)

    # ---------- Chunk ----------
    def add_chunk(self, doc_id: str, chunk: dict[str, Any]):
        q = (
            "MATCH (d:Document {id:$doc_id})\n"
            "MERGE (c:Chunk {id:$id}) SET c += $props\n"
            "MERGE (c)-[:PART_OF]->(d)"
        )
        with self.driver.session() as s:
            s.run(q, doc_id=doc_id, id=chunk["id"], props=chunk)

    # ---------- Indicator ----------
    def add_indicator(self, ind: dict[str, Any], doc_id: str, context_chunk_id: str = None):
        q = (
            "MERGE (i:Indicator {value:$value}) "
            "SET i.type=$type, "
            "    i.firstSeen=coalesce(i.firstSeen,$firstSeen), "
            "    i.lastSeen=$lastSeen\n"
            "WITH i\n"
            "MATCH (d:Document {id:$doc_id})\n"
            "MERGE (i)-[r:MENTIONED_IN {confidence:$confidence}]->(d)\n"
            "SET r.contextChunkId=$context_chunk_id, r.ts=timestamp()"
        )
        with self.driver.session() as s:
            s.run(
                q,
                value=ind["value"],
                type=ind["type"],
                firstSeen=ind.get("firstSeen"),
                lastSeen=ind.get("lastSeen"),
                confidence=ind.get("confidence", 0.9),
                doc_id=doc_id,
                context_chunk_id=context_chunk_id,
            )

    # ---------- Relationships ----------
    def relate(self, a_value: str, b_value: str, rel: str = "RELATED_TO"):
        q = (
            "MATCH (a:Indicator {value:$a}), (b:Indicator {value:$b})\n"
            f"MERGE (a)-[:{rel}]->(b)"
        )
        with self.driver.session() as s:
            s.run(q, a=a_value, b=b_value)

    # ---------- Search ----------
    def vector_search(self, query_vec: list[float], k: int = 10):
        q = (
            "CALL db.index.vector.queryNodes('chunk_vec', $k, $vec) YIELD node, score\n"
            "RETURN node as chunk, score ORDER BY score DESC"
        )
        with self.driver.session() as s:
            return [
                dict(record["chunk"], _score=record["score"])
                for record in s.run(q, k=k, vec=query_vec)
            ]

    def hybrid_search(self, text: str, query_vec: list[float], k: int = 10):
        # Simple hybrid: vector + keyword; rank by combined score
        q = (
            "CALL db.index.vector.queryNodes('chunk_vec', $k, $vec) YIELD node, score\n"
            "WITH node, score\n"
            "WHERE toLower(node.text) CONTAINS toLower($text) OR score >= 0\n"
            "RETURN node as chunk, score ORDER BY score DESC LIMIT $k"
        )
        with self.driver.session() as s:
            return [
                dict(record["chunk"], _score=record["score"])
                for record in s.run(q, text=text, vec=query_vec, k=k)
            ]

    # ---------- Indicator Queries ----------
    def indicator_lookup(self, typ: str):
        q = "MATCH (i:Indicator {type:$typ}) RETURN i.value AS value, i.type AS type"
        with self.driver.session() as s:
            return [dict(r) for r in s.run(q, typ=typ)]

    def context_for_indicator(self, value: str):
        q = (
            "MATCH (i:Indicator {value:$v})-[r:MENTIONED_IN]->(d:Document)\n"
            "OPTIONAL MATCH (c:Chunk {id:r.contextChunkId})\n"
            "RETURN d.id AS documentId, c.text AS chunkText, "
            "r.confidence AS confidence, r.ts AS ts"
        )
        with self.driver.session() as s:
            return [dict(r) for r in s.run(q, v=value)]

    def relationships(self, value: str, hops: int = 1):
        q = (
            f"MATCH (i:Indicator {{value:$v}})-[*1..{hops}]-(j:Indicator) "
            "RETURN DISTINCT j.value AS value, labels(j) AS labels"
        )
        with self.driver.session() as s:
            return [dict(r) for r in s.run(q, v=value)]

    def network(self, value: str, hops: int = 1):
        q = (
            f"MATCH p=(i:Indicator {{value:$v}})-[*1..{hops}]-(j:Indicator) "
            "RETURN p LIMIT 500"
        )
        with self.driver.session() as s:
            paths = s.run(q, v=value).value()
            nodes, links = {}, []
            for p in paths:
                for n in p.nodes:
                    nodes[n.element_id] = {
                        "id": n.element_id,
                        "value": n.get("value", n.get("id")),
                        "label": list(n.labels)[0],
                    }
                for r in p.relationships:
                    links.append({
                        "source": r.start_node.element_id,
                        "target": r.end_node.element_id,
                        "type": r.type,
                    })
            return {"nodes": list(nodes.values()), "links": links}
