import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_uri: str = Field(default="bolt://neo4j:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    embed_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2",alias="EMBED_MODEL")
    m_embed_model: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", alias="MULTILINGUAL_EMBED_MODEL")
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")
    data_dir:str = Field(os.path.join(os.path.dirname(__file__), "..", "data"), alias='DATA_DIR')

settings = Settings()