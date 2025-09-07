import os
import re

from tqdm import tqdm

from src.config import settings
from src.embedding.nlp import Embedder
from src.extraction.indicators import extract_indicators
from src.ingest.ingest import ingest_pdf
from src.preprocessing.chunking import chunk_text
from src.storage.graph_db import Graph


def clean_campaign_name(filename: str) -> str:
    """Infer campaign name from PDF filename."""
    base = os.path.splitext(os.path.basename(filename))[0]
    # replace separators with spaces
    base = base.replace("_", " ").replace("-", " ")
    # look for tokens like 'storm-1516' or 'doppelganger'
    m = re.search(r"(storm[-\s]?\d+|doppelganger|secondaryops)", base, re.I)
    if m:
        return m.group(1).replace(" ", "-").capitalize()
    # fallback: use last word capitalized
    return base.split()[-1].capitalize()


def process_pdf(graph: Graph, filepath:str, doc_id:str, embedder: Embedder, campaign: str = None):
    # 1. ingest pdf file
    docs = ingest_pdf(filepath=filepath)
    
    # 2. Make it into smaller chunks
    chunks = chunk_text(docs)
    
    # 3. Use nlp to embed chunks (vectorization)
    vecs = embedder.embed([c["text"] for c in chunks])
    
    # 4. insert document to graph db
    graph.upsert_document({"id": doc_id, "path": filepath})
    
    if campaign:
        with graph.driver.session() as s:
            s.run("MERGE (c:Campaign {name:$n})", n=campaign)
            s.run("MATCH (d:Document {id:$id}),(c:Campaign {name:$n}) MERGE (d)-[:PART_OF_CAMPAIGN]->(c)", id=doc_id, n=campaign)
    
    for c, v in tqdm(list(zip(chunks, vecs)), desc=f"Load {doc_id}"):
        props = {"id": c["id"], "text": c["text"], "embedding": v}
        graph.add_chunk(doc_id, props)
        # indicators per chunk
        inds = extract_indicators(c["text"])
        # print(inds)
        for ind in inds:
            graph.add_indicator(ind, doc_id, context_chunk_id=c["id"])
            
    return {"chunks": len(chunks)}


def process_pdfs(graph: Graph, pdf_paths, embedder: Embedder):
    stats = {}
    for i, pdf in enumerate(pdf_paths):
        doc_id = os.path.splitext(os.path.basename(pdf))[0]
        # campaign = campaigns[i] if campaigns and i < len(campaigns) else None
        if pdf.lower().endswith(".pdf"):
            path = os.path.join(settings.data_dir, pdf)
            campaign = clean_campaign_name(pdf)
            stats[doc_id] = process_pdf(graph=graph, filepath=path, doc_id=doc_id, embedder=embedder, campaign=campaign)
  
    
def run_pipeline():
    print("---- Pipeline Started -------")
    
    # 1. processing pdfs
    pdf_paths = os.listdir(settings.data_dir)
    g = Graph()
    g.init_schema()
    emb = Embedder()
    process_pdfs(pdf_paths=pdf_paths, graph=g, embedder=emb)


if __name__== "__main__":
    run_pipeline()
    
    