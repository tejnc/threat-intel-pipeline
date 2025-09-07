from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import settings


def chunk_text(docs: list) -> list[dict]:
    """Chunk PDF into overlapping windows with LangChain splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", " ", ""],  # coarse-to-fine split
    )
    chunks = splitter.split_documents(docs)

    results = []
    for idx, c in enumerate(chunks):
        results.append({
            "id": f"chunk-{idx}",
            "text": c.page_content.strip(),
            "metadata": c.metadata,
        })
    return results