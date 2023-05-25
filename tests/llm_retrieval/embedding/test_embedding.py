import os
import asyncio

import pytest

from llm_retrieval.configuration import Configuration
from llm_retrieval.embedding.factory import get_embedding_client
from llm_retrieval.embedding.provider.openai import OpenAIEmbeddingClient


@pytest.fixture
def real_openai_api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key is None:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return key


@pytest.fixture
def fake_openai_api_key():
    return "fake-openai-api-key"


def test_get_embedding_client(fake_openai_api_key):
    configuration = Configuration(
        embedding_model_name="text-embedding-ada-002",
    )
    configuration.set_openai_api_key_callback(lambda: fake_openai_api_key)
    actual = get_embedding_client(configuration)
    assert isinstance(actual, OpenAIEmbeddingClient)
    assert actual.engine == configuration.embedding_model_name


@pytest.mark.billable
def test_openai_embed_batch_async(real_openai_api_key):
    model = "text-embedding-ada-002"
    client = OpenAIEmbeddingClient(real_openai_api_key, model)
    texts = ["Hello world", "Goodbye world"]
    actual = asyncio.run(client.embed_batch_async(texts))
    assert len(actual) == len(texts)
    assert all(len(a) == 1536 for a in actual)
