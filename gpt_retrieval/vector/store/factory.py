from typing import Callable

from gpt_retrieval.vector.store.provider.base import VectorStore
from gpt_retrieval.vector.store.provider.pinecone import PineconeVectorStore


VectorStoreBuilder = Callable[..., VectorStore]
pinecone_vector_store_builder: VectorStoreBuilder = lambda **kwargs: PineconeVectorStore(**kwargs)


vector_store_builder_by_name: dict[str, VectorStoreBuilder] = {
    'pinecone': pinecone_vector_store_builder,
}


def get_vector_store(name: str, **kwargs) -> VectorStore:
    vector_store_builder = vector_store_builder_by_name.get(name)
    if vector_store_builder is None:
        raise ValueError(f"Unknown vector store {name}")
    return vector_store_builder(**kwargs)
