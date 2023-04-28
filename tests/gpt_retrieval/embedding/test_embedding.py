import os
import asyncio

import pytest

from gpt_retrieval.embedding.factory import get_embedding_provider
from gpt_retrieval.embedding.provider.openai import OpenAIEmbeddingProvider


@pytest.fixture
def openai_api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key is None:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return key


def test_get_embedding_provider():
    api_key = "fake-api-key"
    model = "text-embedding-ada-002"
    actual = get_embedding_provider(model, api_key=api_key)
    assert isinstance(actual, OpenAIEmbeddingProvider)
    assert actual.engine == model


@pytest.mark.billable
def test_openai_embed_batch_async(openai_api_key):
    model = "text-embedding-ada-002"
    provider = OpenAIEmbeddingProvider(openai_api_key, model)
    texts = ["Hello world", "Goodbye world"]
    actual = asyncio.run(provider.embed_batch_async(texts))
    assert len(actual) == len(texts)
    assert all(len(a) == 1536 for a in actual)
