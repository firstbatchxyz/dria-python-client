from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, List

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from dria.exceptions import DriaParameterError


class Models(str, Enum):
    jina_embeddings_v2_base_en = 'jina-embeddings-v2-base-en'
    jina_embeddings_v2_small_en = 'jina-embeddings-v2-small-en'
    text_embedding_ada_002 = 'text-embedding-ada-002'
    text_embedding_3_small = 'text-embedding-3-small'
    text_embedding_3_large = 'text-embedding-3-large'
    bge_base_en = 'BAAI/bge-base-en-v1.5'
    bge_base_large = 'BAAI/bge-large-en-v1.5'


@dataclass_json
@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict


class SearchRequest(BaseModel):
    query: str
    contract_id: str
    top_n: int
    field: Optional[str] = None
    model: str
    rerank: Optional[bool] = None
    level: Optional[int] = 2

    def to_json(self):
        return self.model_dump()

    @field_validator('top_n')
    def check_top_n(cls, v: int) -> int:
        if v > 20:
            raise DriaParameterError('top_n cannot be more than 20.')
        return v

    @field_validator('model')
    def check_model(cls, v: str) -> str:
        if v not in [x.value for x in Models]:
            raise DriaParameterError(f"'{v}' is not a valid model enum value.")
        return v

    @field_validator('level')
    def check_level(cls, v: int) -> int:
        if v not in [0, 1, 2, 3, 4]:
            raise DriaParameterError(f"'{v}' is not a valid level value")
        return v


class CreateIndex(BaseModel):
    name: str
    embedding: str
    category: str
    description: str

    def to_json(self):
        return self.model_dump()


@dataclass_json
@dataclass
class QueryResult:
    id: str
    score: float
    metadata: Dict


class QueryRequest(BaseModel):
    vector: List[float]
    contract_id: str
    top_n: int = 10
    level: int = 2

    def to_json(self):
        return self.model_dump()

    @field_validator('top_n')
    def check_top_n(cls, v: int) -> int:
        if v > 20:
            raise ValueError('top_n cannot be more than 20.')
        return v


class FetchResult(BaseModel):
    vectors: List
    metadata: Dict

    def to_json(self):
        return self.model_dump()


class FetchRequest(BaseModel):
    id: List[int]
    contract_id: str

    def to_json(self):
        return self.model_dump()


class VectorInsertRequest(BaseModel):
    data: str
    write_blockchain: bool
    contract_id: str
    batch_size: int

    def to_json(self):
        return self.model_dump()


class TextInsertRequest(BaseModel):
    data: str
    write_blockchain: bool
    model: str
    contract_id: str
    batch_size: int

    def to_json(self):
        return self.model_dump()


class InsertResponse(BaseModel):
    message: str


class CreateIndexResponse(BaseModel):
    contract_id: str


class ContractDefinition(BaseModel):
    contract_id: str
    name: str
    description: str
    category: str

    def to_json(self):
        return self.model_dump()


class ListContracts(BaseModel):
    contracts: List[ContractDefinition]

class Entry(BaseModel):
    entry_count: int
