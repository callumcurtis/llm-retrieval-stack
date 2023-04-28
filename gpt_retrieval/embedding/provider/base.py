import abc

from gpt_retrieval.embedding import Embedding


class EmbeddingProvider(abc.ABC):
    EMBED_BATCH_SIZE: int

    async def embed_batch_async(self, texts: list[str]) -> list[Embedding]:
        """
        Takes in a list of texts and returns a list of embeddings.
        """
        return await self._embed_batch_async(texts)

    @abc.abstractmethod
    async def _embed_batch_async(self, texts: list[str]) -> list[Embedding]:
        pass
