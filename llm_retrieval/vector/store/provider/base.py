import abc

from llm_retrieval.vector.store import StoredVector


class VectorStoreClient(abc.ABC):
    UPSERT_BATCH_SIZE: int

    async def upsert_batch_async(self, vectors: list[StoredVector]) -> None:
        """Takes in a list of vectors and updates/inserts them into the database."""
        await self._upsert_batch_async(vectors)

    @abc.abstractmethod
    async def _upsert_batch_async(self, vectors: list[StoredVector]) -> None:
        pass
