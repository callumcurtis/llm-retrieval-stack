from typing import Callable

from gpt_retrieval.embedding.provider.base import EmbeddingProvider
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingModel
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingProvider


EmbeddingProviderBuilder = Callable[..., EmbeddingProvider]
openai_embedding_provider_builder: EmbeddingProviderBuilder = lambda model, **kwargs: OpenAIEmbeddingProvider(kwargs['api_key'], model)


embedding_provider_builder_by_model: dict[str, EmbeddingProviderBuilder] = {
    **{model.value: openai_embedding_provider_builder for model in OpenAIEmbeddingModel},
}


def get_embedding_provider(model: str, **kwargs) -> EmbeddingProvider:
    embedding_provider_builder = embedding_provider_builder_by_model.get(model)
    if embedding_provider_builder is None:
        raise ValueError(f"Unknown model {model}")
    return embedding_provider_builder(model, **kwargs)
