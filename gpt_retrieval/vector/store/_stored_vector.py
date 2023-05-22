import pydantic

from gpt_retrieval.vector import Vector


class StoredVectorMetadata(pydantic.BaseModel):
    pass


class StoredVector(pydantic.BaseModel):
    id: str
    vector: Vector
    metadata: StoredVectorMetadata
