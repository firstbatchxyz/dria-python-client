from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class QueryResult:
    id: str
    score: float
    metadata: Dict


class QueryRequest(BaseModel):
    vector: List[float]
    top_n: int = 10
    level: int = 2
    query: Optional[str] = None

    def to_json(self):
        return self.model_dump()

    @field_validator('top_n')
    def check_top_n(cls, v: int) -> int:
        if v > 20:
            raise ValueError('top_n cannot be more than 20.')
        return v


class FetchResult(BaseModel):
    metadata: Dict

    def to_json(self):
        return self.model_dump()


class FetchRequest(BaseModel):
    id: List[int]

    def to_json(self):
        return self.model_dump()


class VectorInsertRequest(BaseModel):
    data: list
    write_blockchain: bool
    batch_size: int

    def to_json(self):
        return self.model_dump()


class InsertResponse(BaseModel):
    message: str
