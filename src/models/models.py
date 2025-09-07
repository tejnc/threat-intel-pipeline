from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: str
    k: int = 10

class IndicatorType(BaseModel):
    type: str


class ContextRequest(BaseModel):
    indicator: str


class NetworkRequest(BaseModel):
    indicator: str
    hops: int = 2