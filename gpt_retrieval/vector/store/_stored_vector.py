from pydantic import BaseModel

from gpt_retrieval.vector import Vector


class StoredVectorMetadata(BaseModel):
    pass


class StoredVector(BaseModel):
    id: str
    vector: Vector
    metadata: StoredVectorMetadata
