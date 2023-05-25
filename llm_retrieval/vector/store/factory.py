from typing import Callable

from llm_retrieval.configuration import Configuration
from llm_retrieval.vector.store.provider.base import VectorStoreClient
from llm_retrieval.vector.store.provider.pinecone import PineconeVectorStoreClient


VectorStoreClientBuilder = Callable[..., VectorStoreClient]
pinecone_vector_store_client_builder: VectorStoreClientBuilder = lambda c: PineconeVectorStoreClient(
    api_key=c.pinecone_api_key,
    environment=c.pinecone_environment,
    dimension=c.pinecone_dimension,
    index_name=c.pinecone_index_name,
    metadata_type=c.pinecone_metadata_type,
)


vector_store_client_builder_by_name: dict[str, VectorStoreClientBuilder] = {
    'pinecone': pinecone_vector_store_client_builder,
}


def get_vector_store_client(configuration: Configuration) -> VectorStoreClient:
    vector_store_client_builder = vector_store_client_builder_by_name.get(configuration.vector_store_provider_name)
    if vector_store_client_builder is None:
        raise ValueError(f"Unknown vector store {configuration.vector_store_provider_name}")
    return vector_store_client_builder(configuration)
