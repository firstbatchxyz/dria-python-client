from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, List, Tuple

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from dria.exceptions import DriaParameterError


class ModelEnum(str, Enum):
    jina_embeddings_v2_base_en = 'jinaai/jina-embeddings-v2-base-en'
    jina_embeddings_v2_small_en = 'jinaai/jina-embeddings-v2-small-en'
    text_embedding_ada_002 = 'openai/text-embedding-ada-002'


@dataclass_json
@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict


@dataclass_json
@dataclass
class SearchRequest(BaseModel):
    query: str
    contract_id: str
    top_n: int
    field: Optional[str] = None
    model: Optional[str] = None
    re_rank: Optional[bool] = None
    level: Optional[int] = None

    def to_json(self):
        return self.model_dump()

    @field_validator('top_n')
    def check_top_n(cls, v: int) -> int:
        if v > 20:
            raise DriaParameterError('top_n cannot be more than 20.')
        return v

    @field_validator('model')
    def check_model(cls, v: str) -> str:
        if v not in ModelEnum.__members__:
            raise DriaParameterError(f"'{v}' is not a valid model enum value.")
        return v

    @field_validator('level')
    def check_level(cls, v: int) -> int:
        if v not in [1, 2, 3, 4]:
            raise DriaParameterError(f"'{v}' is not a valid level value")
        return v


@dataclass_json
@dataclass
class QueryResult:
    id: str
    score: float
    metadata: Dict


@dataclass_json
@dataclass
class QueryRequest(BaseModel):
    vector: List[float]
    contract_id: str
    top_n: int = 10

    def to_json(self):
        return self.model_dump()

    @field_validator('top_n')
    def check_top_n(cls, v: int) -> int:
        if v > 20:
            raise ValueError('top_n cannot be more than 20.')
        return v


@dataclass_json
@dataclass
class FetchResult(BaseModel):
    id: int
    metadata: Dict


@dataclass_json
@dataclass
class FetchRequest(BaseModel):
    id: int
    contract_id: str

    def to_json(self):
        return self.model_dump()


@dataclass_json
@dataclass
class FetchResponse(BaseModel):
    results: List[FetchResult]

    def __init__(self, results: Tuple[List[int], List[Dict]]):
        self.results = [FetchResult(id=id_, metadata=metadata) for id_, metadata in zip(*results)]

    def __iter__(self):
        return iter(self.results)


@dataclass_json
@dataclass
class InsertRequest(BaseModel):
    data: str
    contract_id: str
    batch_size: int

    def to_json(self):
        return self.model_dump()


@dataclass_json
@dataclass
class InsertResponse(BaseModel):
    id: int
