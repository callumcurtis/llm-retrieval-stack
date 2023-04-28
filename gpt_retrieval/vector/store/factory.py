from typing import Callable

from gpt_retrieval.vector.store.provider.base import VectorStoreClient
from gpt_retrieval.vector.store.provider.pinecone import PineconeVectorStoreClient


VectorStoreClientBuilder = Callable[..., VectorStoreClient]
pinecone_vector_store_client_builder: VectorStoreClientBuilder = lambda **kwargs: PineconeVectorStoreClient(**kwargs)


vector_store_client_builder_by_name: dict[str, VectorStoreClientBuilder] = {
    'pinecone': pinecone_vector_store_client_builder,
}


def get_vector_store_client(name: str, **kwargs) -> VectorStoreClient:
    vector_store_client_builder = vector_store_client_builder_by_name.get(name)
    if vector_store_client_builder is None:
        raise ValueError(f"Unknown vector store {name}")
    return vector_store_client_builder(**kwargs)
