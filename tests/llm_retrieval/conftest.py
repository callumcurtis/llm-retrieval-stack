import pytest
from unittest.mock import create_autospec

from llm_retrieval.vector.store.provider.base import VectorStoreClient
from llm_retrieval.embedding.provider.base import EmbeddingClient


UTF8_CHARS = [
    b'\x00',
    b'\x7f',
    b'\xc2\x80',
    b'\xdf\xbf',
    b'\xe0\xa0\x80',
    b'\xef\xbf\xbf',
    b'\xf0\x90\x80\x80',
    b'\xf4\x8f\xbf\xbf',
]


def truncations(char: bytes):
    return (char[:i] for i in range(1, len(char)))


def splits(char: bytes):
    return ((char[:i], char[i:]) for i in range(1, len(char)))


@pytest.fixture(params=UTF8_CHARS)
def utf8_char(request):
    return request.param


@pytest.fixture(params=(t for c in UTF8_CHARS for t in truncations(c)))
def utf8_truncation(request):
    return request.param


@pytest.fixture(params=(s for c in UTF8_CHARS for s in splits(c)))
def utf8_split(request):
    return request.param


@pytest.fixture
def mock_embedding_client_factory():

    async def embed_batch_async(texts):
        return [[1.0]] * len(texts)

    def factory():
        m = create_autospec(EmbeddingClient)
        m.EMBED_BATCH_SIZE = 21344
        m.embed_batch_async.side_effect = embed_batch_async
        return m
    
    return factory


@pytest.fixture
def mock_vector_store_client_factory():

    def factory():
        m = create_autospec(VectorStoreClient)
        m.UPSERT_BATCH_SIZE = 16234
        m.upsert_batch_async.return_value = None
        return m
    
    return factory
