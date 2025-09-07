from langchain_community.document_loaders import PyPDFLoader


# ingestion of pdfs
def ingest_pdf(filepath:str) -> list:
    docs = []
    loader = PyPDFLoader(filepath)
    docs.extend(loader.load())
    return docs
