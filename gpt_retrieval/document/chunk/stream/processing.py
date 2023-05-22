import itertools
from typing import Iterable, Union

from gpt_retrieval.utils.common.iterable import batched
from gpt_retrieval.utils.common.iterable import ConcurrentAsyncMapper
from gpt_retrieval.document.chunk import DecodedChunk
from gpt_retrieval.embedding.provider.base import EmbeddingClient
from gpt_retrieval.vector.store.provider.base import VectorStoreClient
from gpt_retrieval.vector.store import StoredVector
from gpt_retrieval.vector.store import StoredVectorMetadata


async def _embed_and_upsert_decoded_chunk_batch_async(
    decoded_chunk_batch: Iterable[DecodedChunk],
    vector_prefix: str,
    metadata: StoredVectorMetadata,
    embedding_client: EmbeddingClient,
    vector_store_client: VectorStoreClient,
) -> None:
    if not decoded_chunk_batch:
        return
    texts = [decoded_chunk.text for decoded_chunk in decoded_chunk_batch]
    embeddings = await embedding_client.embed_batch_async(texts)
    stored_vectors = [
        StoredVector(
            id = f'{vector_prefix}:{decoded_chunk.start}-{decoded_chunk.end}',
            vector=embedding,
            metadata=metadata,
        )
        for embedding, decoded_chunk in zip(embeddings, decoded_chunk_batch)
    ]
    await vector_store_client.upsert_batch_async(stored_vectors)


def embed_and_upsert_decoded_chunk_stream(
    decoded_chunk_stream: Iterable[DecodedChunk],
    vector_prefixes: Union[str, Iterable[str]],
    metadata: Union[StoredVectorMetadata, Iterable[StoredVectorMetadata]],
    embedding_client: EmbeddingClient,
    vector_store_client: VectorStoreClient,
    max_concurrent_batches: int,
    batch_size: int = None,
) -> None:
    assert batch_size is None or batch_size > 0
    assert max_concurrent_batches > 0

    max_batch_size = min(embedding_client.EMBED_BATCH_SIZE, vector_store_client.UPSERT_BATCH_SIZE)
    if batch_size is None:
        batch_size = max_batch_size
    assert batch_size <= max_batch_size

    if isinstance(vector_prefixes, str):
        vector_prefixes = itertools.repeat(vector_prefixes)

    if isinstance(metadata, StoredVectorMetadata):
        metadata = itertools.repeat(metadata)

    vector_prefixes = iter(vector_prefixes)
    metadata = iter(metadata)

    async def _embed_and_upsert_decoded_chunk_batch_async_wrapper(decoded_chunk_batch: Iterable[DecodedChunk]) -> None:
        await _embed_and_upsert_decoded_chunk_batch_async(
            decoded_chunk_batch,
            vector_prefix=next(vector_prefixes),
            metadata=next(metadata),
            embedding_client=embedding_client,
            vector_store_client=vector_store_client,
        )

    mapper = ConcurrentAsyncMapper(
        _embed_and_upsert_decoded_chunk_batch_async_wrapper,
        max_concurrent_batches,
    )

    mapper(batched(decoded_chunk_stream, batch_size))
