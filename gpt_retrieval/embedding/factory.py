from typing import Callable

from gpt_retrieval.embedding.provider.base import EmbeddingClient
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingModel
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingClient


EmbeddingClientBuilder = Callable[..., EmbeddingClient]
openai_embedding_client_builder: EmbeddingClientBuilder = lambda model, **kwargs: OpenAIEmbeddingClient(**kwargs, engine=model)


embedding_client_builder_by_model: dict[str, EmbeddingClientBuilder] = {
    **{model.value: openai_embedding_client_builder for model in OpenAIEmbeddingModel},
}


def get_embedding_client(model: str, **kwargs) -> EmbeddingClient:
    embedding_client_builder = embedding_client_builder_by_model.get(model)
    if embedding_client_builder is None:
        raise ValueError(f"Unknown model {model}")
    return embedding_client_builder(model, **kwargs)
