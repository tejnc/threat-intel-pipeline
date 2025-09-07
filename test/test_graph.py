import pytest
from src.storage.graph_db import Graph
from src.embedding.nlp import Embedder

@pytest.fixture(scope="module")
def graph():
    g = Graph()
    g.init_schema()
    yield g
    g.close()

@pytest.fixture(scope="module")
def embedder():
    return Embedder()

@pytest.fixture(scope="module")
def prepared_graph(graph, embedder):
    # Create document + chunk once
    doc = {"id": "doc_test_1", "title": "Unit Test Doc"}
    graph.upsert_document(doc)

    chunk = {
        "id": "doc_test_1_0",
        "text": "This is a test chunk for unit testing.",
        "embedding": embedder.embed(["This is a test chunk for unit testing."])[0]
    }
    graph.add_chunk(doc_id=doc["id"], chunk=chunk)
    return graph


def test_add_chunk(prepared_graph):
    with prepared_graph.driver.session() as s:
        res = s.run("MATCH (c:Chunk {id:$cid}) RETURN c", cid="doc_test_1_0").single()
        assert res is not None

def test_semantic_search_returns_results(prepared_graph, embedder):
    query = "test"
    vec = embedder.embed([query])[0]
    results = prepared_graph.hybrid_search(query, vec, k=2)
    assert isinstance(results, list)
    assert len(results) > 0
