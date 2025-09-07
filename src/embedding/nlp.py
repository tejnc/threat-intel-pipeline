from langdetect import detect
from sentence_transformers import SentenceTransformer

from src.config import settings


class Embedder:
    def __init__(self):
        self.en = SentenceTransformer(settings.embed_model, device='cpu')
        self.en = SentenceTransformer(settings.m_embed_model, device='cpu')
        
    def embed(self, texts:list[str]):
        try:
            langs = set()
            for t in texts:
                try:
                    langs.add(detect(t))
                except Exception as e:
                    raise f"error found {e}"
            model = self.multi if any(l in {"fr", "de", "ru", "uk", "pl", "it","es"} for l in langs) else self.en
        except Exception:
            model = self.en
        vecs = model.encode(texts, normalize_embeddings=True)
        return vecs.tolist()