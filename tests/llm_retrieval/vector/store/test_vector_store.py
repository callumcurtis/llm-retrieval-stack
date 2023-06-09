import os
import asyncio

import pytest
import pinecone
from tenacity import retry, stop_after_attempt, wait_exponential

from llm_retrieval.configuration import Configuration
from llm_retrieval.vector.store import StoredVector
from llm_retrieval.vector.store import StoredVectorMetadata
from llm_retrieval.vector.store.factory import get_vector_store_client
from llm_retrieval.vector.store.provider.pinecone import PineconeVectorStoreClient


@pytest.fixture
def pinecone_api_key():
    key = os.environ.get("PINECONE_API_KEY")
    if key is None:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    return key


@pytest.fixture
def pinecone_environment():
    environment = os.environ.get("PINECONE_ENVIRONMENT")
    if environment is None:
        raise ValueError("PINECONE_ENVIRONMENT environment variable not set")
    return environment


@pytest.fixture
def pinecone_index_name():
    return "test"


@pytest.fixture
def pinecone_dimension():
    return 1536


@pytest.fixture
def init_pinecone_client(pinecone_api_key, pinecone_environment):
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)


@pytest.fixture
def remove_pinecone_index_before_and_after_test(init_pinecone_client, pinecone_index_name):
    def delete_index_if_exists():
        if pinecone_index_name in pinecone.list_indexes():
            pinecone.delete_index(pinecone_index_name)

    delete_index_if_exists()
    yield
    delete_index_if_exists()


@pytest.fixture
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def pinecone_index(
    remove_pinecone_index_before_and_after_test,
    pinecone_index_name,
    pinecone_dimension,
):
    pinecone.create_index(
        pinecone_index_name,
        dimension=pinecone_dimension,
    )
    index = pinecone.Index(pinecone_index_name)
    # Make a request to ensure the index is ready.
    # Fixes an issue where upsert requests fail with a 503 error.
    index.describe_index_stats()
    return index


@pytest.mark.billable
@pytest.mark.slow
def test_get_pinecone_vector_store_client(
    remove_pinecone_index_before_and_after_test,
    pinecone_api_key,
    pinecone_dimension,
    pinecone_index_name,
    pinecone_environment,
):
    configuration = Configuration(
        vector_store_provider_name='pinecone',
        pinecone_api_key=pinecone_api_key,
        pinecone_environment=pinecone_environment,
        pinecone_index_name=pinecone_index_name,
        pinecone_dimension=pinecone_dimension,
        pinecone_metadata_type=StoredVectorMetadata,
    )
    actual = get_vector_store_client(configuration)
    assert isinstance(actual, PineconeVectorStoreClient)
    assert actual.metadata_type == configuration.pinecone_metadata_type
    assert actual.environment == configuration.pinecone_environment
    assert actual.dimension == configuration.pinecone_dimension
    index_details = pinecone.describe_index(pinecone_index_name)
    assert index_details.name == configuration.pinecone_index_name
    assert index_details.dimension == configuration.pinecone_dimension


class FakeStoredVectorMetadata(StoredVectorMetadata):
    foo: str
    bar: int
    quuz: float


@pytest.mark.billable
@pytest.mark.slow
def test_pinecone_vector_store_client_upsert_batch_async(
    pinecone_index,
    pinecone_api_key,
    pinecone_environment,
    pinecone_dimension,
    pinecone_index_name,
):
    client = PineconeVectorStoreClient(
        api_key=pinecone_api_key,
        environment=pinecone_environment,
        dimension=pinecone_dimension,
        index_name=pinecone_index_name,
        metadata_type=FakeStoredVectorMetadata,
    )
    stored_vectors = [
        StoredVector(
            id="1",
            vector=[1.0] * pinecone_dimension,
            metadata=FakeStoredVectorMetadata(foo="foo-1", bar=1, quuz=1.0),
        ),
        StoredVector(
            id="2",
            vector=[2.0] * pinecone_dimension,
            metadata=FakeStoredVectorMetadata(foo="foo-2", bar=2, quuz=2.0),
        ),
        StoredVector(
            id="3",
            vector=[3.0] * pinecone_dimension,
            metadata=FakeStoredVectorMetadata(foo="foo-3", bar=3, quuz=3.0),
        ),
    ]
    actual = asyncio.run(client.upsert_batch_async(stored_vectors))
    assert actual is None
    index_stats = pinecone_index.describe_index_stats()
    assert index_stats.total_vector_count == len(stored_vectors)
    fetched_stored_vectors = pinecone_index.fetch(ids=[sv.id for sv in stored_vectors]).vectors
    fetched_stored_vectors = sorted(fetched_stored_vectors.values(), key=lambda sv: sv.id)
    assert len(fetched_stored_vectors) == len(stored_vectors)
    for stored_vector, fetched_stored_vector in zip(stored_vectors, fetched_stored_vectors):
        assert stored_vector.id == fetched_stored_vector.id
        assert stored_vector.vector == fetched_stored_vector.values
        assert stored_vector.metadata.dict() == fetched_stored_vector.metadata
