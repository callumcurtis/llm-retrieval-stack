import abc


class EmbeddingProvider(abc.ABC):

    async def embed_batch_async(self, texts: list[str]) -> list[list[float]]:
        """
        Takes in a list of texts and returns a list of embeddings.
        """
        return await self._embed_batch_async(texts)

    @abc.abstractmethod
    async def _embed_batch_async(self, texts: list[str]) -> list[list[float]]:
        pass
