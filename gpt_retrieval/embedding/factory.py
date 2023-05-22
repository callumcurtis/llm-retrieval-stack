from typing import Callable

from gpt_retrieval.configuration import Configuration
from gpt_retrieval.embedding.provider.base import EmbeddingClient
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingModel
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingClient


EmbeddingClientBuilder = Callable[..., EmbeddingClient]
openai_embedding_client_builder: EmbeddingClientBuilder = lambda c: OpenAIEmbeddingClient(api_key=c.openai_api_key, engine=c.embedding_model_name)


embedding_client_builder_by_model: dict[str, EmbeddingClientBuilder] = {
    **{model.value: openai_embedding_client_builder for model in OpenAIEmbeddingModel},
}


def get_embedding_client(configuration: Configuration) -> EmbeddingClient:
    embedding_client_builder = embedding_client_builder_by_model.get(configuration.embedding_model_name)
    if embedding_client_builder is None:
        raise ValueError(f"Unknown model {configuration.embedding_model_name}")
    return embedding_client_builder(configuration)
